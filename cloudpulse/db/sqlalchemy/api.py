# Copyright 2013 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""SQLAlchemy storage backend."""

from cloudpulse.common import exception
from cloudpulse.common.plugin import discover
from cloudpulse.common import utils
from cloudpulse.db import api
from cloudpulse.db.sqlalchemy import models
from cloudpulse.openstack.common._i18n import _
from cloudpulse.openstack.common import log
from cloudpulse.scenario import base
from oslo_config import cfg
from oslo_db import exception as db_exc
from oslo_db.sqlalchemy import session as db_session
from oslo_db.sqlalchemy import utils as db_utils
from oslo_utils import timeutils
import sqlalchemy.orm.exc

CONF = cfg.CONF


LOG = log.getLogger(__name__)


_FACADE = None


def _create_facade_lazily():
    global _FACADE
    if _FACADE is None:
        _FACADE = db_session.EngineFacade.from_config(CONF)
    return _FACADE


def get_engine():
    facade = _create_facade_lazily()
    return facade.get_engine()


def get_session(**kwargs):
    facade = _create_facade_lazily()
    return facade.get_session(**kwargs)


def get_backend():
    """The backend is this module itself."""
    return Connection()


def model_query(model, *args, **kwargs):
    """Query helper for simpler session usage.

    :param session: if present, the session to use
    """

    session = kwargs.get('session') or get_session()
    query = session.query(model, *args)
    return query


def add_identity_filter(query, value):
    """Adds an identity filter to a query.

    Filters results by ID, if supplied value is a valid integer.
    Otherwise attempts to filter results by UUID.

    :param query: Initial query to add filter to.
    :param value: Value for filtering results by.
    :return: Modified query.
    """
    if utils.is_int_like(value):
        return query.filter_by(id=value)
    elif utils.is_uuid_like(value):
        return query.filter_by(uuid=value)
    else:
        raise exception.InvalidIdentity(identity=value)


def _paginate_query(model, limit=None, marker=None, sort_key=None,
                    sort_dir=None, query=None):
    if not query:
        query = model_query(model)
    sort_keys = ['id']
    if sort_key and sort_key not in sort_keys:
        sort_keys.insert(0, sort_key)
    query = db_utils.paginate_query(query, model, limit, sort_keys,
                                    marker=marker, sort_dir=sort_dir)
    return query.all()


class Connection(api.Connection):

    """SqlAlchemy connection."""

    def __init__(self):
        pass

    def _add_tenant_filters(self, context, query):
        if context.project_id:
            query = query.filter_by(project_id=context.project_id)
        else:
            query = query.filter_by(user_id=context.user_id)

        return query

    def _add_tests_filters(self, query, filters):
        if filters is None:
            filters = []

        if 'name' in filters:
            query = query.filter_by(name=filters['name'])

        return query

    def get_test_list(self, context, filters=None, limit=None, marker=None,
                      sort_key=None, sort_dir=None):
        # query = model_query(models.cpulse)
        query = model_query(models.cpulse)
        query = self._add_tests_filters(query, filters)
        return _paginate_query(models.cpulse, limit, marker,
                               sort_key, sort_dir, query)

    def create_test(self, values):
        # ensure that  the test name is valid
        discover.import_modules_from_package("cloudpulse.scenario.plugins")
        plugins = discover.itersubclasses(base.Scenario)
        if not any(values['name'] in dir(scenario) for scenario in plugins):
            raise exception.TestInvalid(test=values['name'])

        # ensure defaults are present for new tests
        if not values.get('uuid'):
            values['uuid'] = utils.generate_uuid()

        cpulse = models.cpulse()
        cpulse.update(values)
        # TODO(VINOD)
        try:
            cpulse.save()
        except db_exc.DBDuplicateEntry:
            raise exception.TestAlreadyExists(uuid=values['uuid'])
        return cpulse

    def get_test_by_id(self, context, test_id):
        query = model_query(models.cpulse)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(id=test_id)
        try:
            return query.one()
        except sqlalchemy.orm.exc.NoResultFound:
            raise exception.TestNotFound(test=test_id)

    def get_test_by_name(self, context, test_name):
        query = model_query(models.cpulse)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(name=test_name)
        try:
            return query.one()
        except sqlalchemy.orm.exc.MultipleResultsFound:
            raise exception.Conflict('Multiple tests exist with same name.'
                                     ' Please use the test uuid instead.')
        except sqlalchemy.orm.exc.NoResultFound:
            raise exception.TestNotFound(test=test_name)

    def get_test_by_uuid(self, context, uuid):
        query = model_query(models.cpulse)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(uuid=uuid)
        try:
            return query.one()
        except sqlalchemy.orm.exc.NoResultFound:
            raise exception.TestNotFound(test=uuid)

    def destroy_test(self, test_id):
        session = get_session()
        test_ref = None
        with session.begin():
            query = model_query(models.cpulse, session=session)
            query = add_identity_filter(query, test_id)

            try:
                test_ref = query.one()
            except sqlalchemy.orm.exc.NoResultFound:
                raise exception.TestNotFound(test=test_id)
            query.delete()

        return test_ref

    def update_test(self, test_id, values):
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing test.")
            raise exception.InvalidParameterValue(err=msg)

        return self._do_update_test(test_id, values)

    def _do_update_test(self, test_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.cpulse, session=session)
            query = add_identity_filter(query, test_id)
            try:
                ref = query.with_lockmode('update').one()
            except sqlalchemy.orm.exc.NoResultFound:
                raise exception.TestNotFound(test=test_id)

            if 'provision_state' in values:
                values['provision_updated_at'] = timeutils.utcnow()

            ref.update(values)
        return ref

    def create_test_lock(self, test_name, conductor_id):
        session = get_session()
        with session.begin():
            query = model_query(models.CpulseLock, session=session)
            lock = query.filter_by(test_name=test_name).first()
            if lock is not None:
                return lock.conductor_id
            session.add(models.CpulseLock(test_name=test_name,
                                          conductor_id=conductor_id))

    def steal_test_lock(self, test_name, old_conductor_id, new_conductor_id):
        session = get_session()
        with session.begin():
            query = model_query(models.CpulseLock, session=session)
            lock = query.filter_by(test_name=test_name).first()
            if lock is None:
                return True
            elif lock.conductor_id != old_conductor_id:
                return lock.conductor_id
            else:
                lock.update({'conductor_id': new_conductor_id})

    def release_test_lock(self, test_name, conductor_id):
        session = get_session()
        with session.begin():
            query = model_query(models.CpulseLock, session=session)
            query = query.filter_by(test_name=test_name,
                                    conductor_id=conductor_id)
            count = query.delete()
            if count == 0:
                return True

    def delete_old_tests(self, num_range,
                         num_tests=cfg.CONF.database.max_db_entries):
        alltests = _paginate_query(models.cpulse)
        if len(alltests) < num_tests:
            return
        session = get_session()
        removable = len(alltests) - num_tests
        num_to_del = (removable if (removable < (3 * num_range))
                      else 3 * num_range)
        with session.begin():
            for i in range(0, num_to_del):
                session.delete(alltests[i])
