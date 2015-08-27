# coding=utf-8
#
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_versionedobjects import fields

from cloudpulse.common import exception
from cloudpulse.common import utils
from cloudpulse.db import api as dbapi
from cloudpulse.objects import base
from cloudpulse.openstack.common._i18n import _LI
from cloudpulse.openstack.common import log as logging
LOG = logging.getLogger(__name__)


class Status(object):
    CREATE_IN_PROGRESS = 'CREATE_IN_PROGRESS'
    CREATE_FAILED = 'CREATE_FAILED'
    CREATED = 'CREATED'
    UPDATE_IN_PROGRESS = 'UPDATE_IN_PROGRESS'
    UPDATE_FAILED = 'UPDATE_FAILED'
    UPDATED = 'UPDATED'
    DELETE_IN_PROGRESS = 'DELETE_IN_PROGRESS'
    DELETE_FAILED = 'DELETE_FAILED'
    DELETED = 'DELETED'


@base.CloudpulseObjectRegistry.register
class Cpulse(base.CloudpulsePersistentObject, base.CloudpulseObject,
             base.CloudpulseObjectDictCompat):
    # Version 1.0: Initial version
    VERSION = '1.0'

    dbapi = dbapi.get_instance()

    fields = {
        'id': fields.IntegerField(),
        'uuid': fields.UUIDField(nullable=True),
        'name': fields.StringField(nullable=True),
        'state': fields.StringField(nullable=True),
        'result': fields.StringField(nullable=True),
        'testtype': fields.StringField(nullable=True)
    }

    @staticmethod
    def _from_db_object(test, db):
        """Converts a database entity to a formal object."""
        for field in test.fields:
            test[field] = db[field]

        test.obj_reset_changes()
        return test

    @staticmethod
    def _from_db_object_list(db_objects, cls, ctx):
        """Converts a list of db entities to a list of formal objects."""
        return [Cpulse._from_db_object(cls(ctx), obj) for obj in db_objects]

    @base.remotable_classmethod
    def get(cls, context, test_id):
        """Find a test based on its id or uuid and return a Cpulse object.

        :param test_id: the id *or* uuid of a test.
        :returns: a :class:`Cpulse` object.
        """
        if utils.is_int_like(test_id):
            return cls.get_by_id(context, test_id)
        elif utils.is_uuid_like(test_id):
            return cls.get_by_uuid(context, test_id)
        else:
            raise exception.InvalidIdentity(identity=test_id)

    @base.remotable_classmethod
    def get_by_id(cls, context, test_id):
        """Find a test based on its integer id and return a Cpulse object.

        :param test_id: the id of a test.
        :returns: a :class:`Cpulse` object.
        """
        db = cls.dbapi.get_test_by_id(context, test_id)
        test = Cpulse._from_db_object(cls(context), db)
        return test

    @base.remotable_classmethod
    def get_by_uuid(cls, context, uuid):
        """Find a test based on uuid and return a :class:`Cpulse` object.

        :param uuid: the uuid of a test.
        :param context: Security context
        :returns: a :class:`Cpulse` object.
        """
        db = cls.dbapi.get_test_by_uuid(context, uuid)
        test = Cpulse._from_db_object(cls(context), db)
        return test

    @base.remotable_classmethod
    def get_by_name(cls, context, name):
        """Find a test based on name and return a Cpulse object.

        :param name: the logical name of a test.
        :param context: Security context
        :returns: a :class:`Cpulse` object.
        """
        db = cls.dbapi.get_test_by_name(context, name)
        test = Cpulse._from_db_object(cls(context), db)
        return test

    @base.remotable_classmethod
    def list(cls, context, limit=None, marker=None,
             sort_key=None, sort_dir=None, filters=None):
        """Return a list of Cpulse objects.

        :param context: Security context.
        :param limit: maximum number of resources to return in a single result.
        :param marker: pagination marker for large data sets.
        :param sort_key: column to sort results by.
        :param sort_dir: direction to sort. "asc" or "desc".
        :returns: a list of :class:`Cpulse` object.

        """
        db = cls.dbapi.get_test_list(context, limit=limit,
                                     marker=marker,
                                     sort_key=sort_key,
                                     sort_dir=sort_dir,
                                     filters=filters)
        return Cpulse._from_db_object_list(db, cls, context)

    @base.remotable
    def create(self, context=None):
        """Create a Cpulse record in the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: Cpulse(context)

        """
        values = self.obj_get_changes()
        LOG.info(_LI('Dumping CREATE test datastructure  %s') % str(values))
        db = self.dbapi.create_test(values)
        self._from_db_object(self, db)

    @base.remotable
    def destroy(self, context=None):
        """Delete the Cpulse from the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: Cpulse(context)
        """
        self.dbapi.destroy_test(self.uuid)
        self.obj_reset_changes()

    @base.remotable
    def save(self, context=None):
        """Save updates to this Cpulse.

        Updates will be made column by column based on the result
        of self.what_changed().

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: Cpulse(context)
        """
        updates = self.obj_get_changes()
        self.dbapi.update_test(self.uuid, updates)

        self.obj_reset_changes()

    @base.remotable
    def refresh(self, context=None):
        """Loads updates for this Cpulse.

        Loads a test with the same uuid from the database and
        checks for updated attributes. Updates are applied from
        the loaded test column by column, if there are any updates.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: Cpulse(context)
        """
        current = self.__class__.get_by_uuid(self._context, uuid=self.uuid)
        for field in self.fields:
            if self.obj_attr_is_set(field) and self[field] != current[field]:
                self[field] = current[field]
