# Copyright 2013 Hewlett-Packard Development Company, L.P.
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

"""
SQLAlchemy models for cloudpulse service
"""

import json

from oslo_config import cfg
from oslo_db import options as db_options
from oslo_db.sqlalchemy import models
from oslo_utils import reflection
import six.moves.urllib.parse as urlparse
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer
from sqlalchemy import schema
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.types import TypeDecorator, TEXT

from cloudpulse.common import paths


sql_opts = [
    cfg.StrOpt('mysql_engine',
               default='InnoDB',
               help='MySQL engine to use.'),
    cfg.IntOpt('max_db_entries',
               default=10,
               help=('Maximum test result entries to be persisted ')),

]

_DEFAULT_SQL_CONNECTION = ('sqlite:///' +
                           paths.state_path_def('cloudpulse.sqlite'))

cfg.CONF.register_opts(sql_opts, 'database')
db_options.set_defaults(cfg.CONF, connection=_DEFAULT_SQL_CONNECTION)


def table_args():
    engine_name = urlparse.urlparse(cfg.CONF.database.connection).scheme
    if engine_name == 'mysql':
        return {'mysql_engine': cfg.CONF.database.mysql_engine,
                'mysql_charset': "utf8"}
    return None


class JsonEncodedType(TypeDecorator):
    """Abstract base type serialized as json-encoded string in db."""
    type = None
    impl = TEXT

    def process_bind_param(self, value, dialect):
        cls_name = reflection.get_class_name(self, fully_qualified=False)
        if value is None:
            # Save default value according to current type to keep the
            # interface the consistent.
            value = self.type()
        elif not isinstance(value, self.type):
            raise TypeError("%s supposes to store %s objects, but %s given"
                            % (cls_name,
                               self.type.__name__,
                               type(value).__name__))
        serialized_value = json.dumps(value)
        return serialized_value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class JSONEncodedDict(JsonEncodedType):
    """Represents dict serialized as json-encoded string in db."""
    type = dict


class JSONEncodedList(JsonEncodedType):
    """Represents list serialized as json-encoded string in db."""
    type = list


class CpulseBase(models.TimestampMixin,
                 models.ModelBase):

    metadata = None

    def as_dict(self):
        d = {}
        for c in self.__table__.columns:
            d[c.name] = self[c.name]
        return d

    def save(self, session=None):
        import cloudpulse.db.sqlalchemy.api as db_api

        if session is None:
            session = db_api.get_session()

        super(CpulseBase, self).save(session)

Base = declarative_base(cls=CpulseBase)


class cpulse(Base):
    """Represents cloudpulse test"""

    __tablename__ = 'cpulse'
    __table_args__ = (
        schema.UniqueConstraint('uuid', name='uniq_test0uuid'),
        table_args()
        )
    id = Column(Integer, primary_key=True)
    uuid = Column(String(64))
    name = Column(String(255))
    state = Column(String(255))
    result = Column(Text)
    testtype = Column(String(255))


class CpulseLock(Base):
    """Represents a cpulselock."""

    __tablename__ = 'cpulselock'
    __table_args__ = (
        schema.UniqueConstraint('test_name', name='uniq_testlock0test_name'),
        table_args()
        )
    id = Column(Integer, primary_key=True)
    test_name = Column(String(64))
    conductor_id = Column(String(64))
