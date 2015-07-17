# Copyright 2010-2011 OpenStack Foundation
# Copyright (c) 2013 Cisco Inc
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

"""Magnum DB test base class."""

import os
import shutil

import fixtures
from oslo_config import cfg

from cloudpulse.common import paths
from cloudpulse.db import api as dbapi
from cloudpulse.db.sqlalchemy import api as sqla_api
from cloudpulse.db.sqlalchemy import models
from cloudpulse.tests import base


CONF = cfg.CONF

CONF.import_opt('enable_authentication', 'cloudpulse.api.auth')

_DB_CACHE = None


class Database(fixtures.Fixture):

    def __init__(self, db_api, sql_connection,
                 sqlite_db, sqlite_clean_db):
        self.sql_connection = sql_connection
        self.sqlite_db = sqlite_db
        self.sqlite_clean_db = sqlite_clean_db

        self.engine = db_api.get_engine()
        self.engine.dispose()
        conn = self.engine.connect()
        if sql_connection == "sqlite://":
            self.setup_sqlite()
        elif sql_connection.startswith('sqlite:///'):
            testdb = paths.state_path_rel(sqlite_db)
            self.setup_sqlite()
        self.post_migrations()
        if sql_connection == "sqlite://":
            conn = self.engine.connect()
            self._DB = "".join(line for line in conn.connection.iterdump())
            self.engine.dispose()
        else:
            cleandb = paths.state_path_rel(sqlite_clean_db)
            shutil.copyfile(testdb, cleandb)

    def setup_sqlite(self):
        models.Base.metadata.create_all(self.engine)

    def setUp(self):
        super(Database, self).setUp()

        if self.sql_connection == "sqlite://":
            conn = self.engine.connect()
            conn.connection.executescript(self._DB)
            self.addCleanup(self.engine.dispose)
        else:
            shutil.copyfile(paths.state_path_rel(self.sqlite_clean_db),
                            paths.state_path_rel(self.sqlite_db))
            self.addCleanup(os.unlink, paths.state_path_rel(self.sqlite_db))

    def post_migrations(self):
        """Any addition steps that are needed outside of the migrations."""


class DbTestCase(base.TestCase):

    def setUp(self):
        cfg.CONF.set_override("enable_authentication", False)
        super(DbTestCase, self).setUp()

        self.dbapi = dbapi.get_instance()

        global _DB_CACHE
        if not _DB_CACHE:
            _DB_CACHE = Database(sqla_api,
                                 sql_connection=CONF.database.connection,
                                 sqlite_db=CONF.database.sqlite_db,
                                 sqlite_clean_db='clean.sqlite')
        self.useFixture(_DB_CACHE)
