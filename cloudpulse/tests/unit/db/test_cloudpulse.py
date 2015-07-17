# Copyright 2010-2011 OpenStack Foundation
# Copyright (c) 2013 Cisco Inc
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


from cloudpulse.common import exception
from cloudpulse.common import utils as cloudpulse_utils
from cloudpulse.tests.unit.db import base
from cloudpulse.tests.unit.db import utils


class TestCloudpulseDB(base.DbTestCase):
    def test_cloudpulse_db(self):
        utils.create_cpulse_test()

    def test_cloudpulse_test_already_exists(self):
        utils.create_cpulse_test()
        self.assertRaises(exception.TestAlreadyExists,
                          utils.create_cpulse_test)

    def test_update_cloudpulse_test(self):
        cpulse = utils.create_cpulse_test()
        new_state = 'running'
        res = self.dbapi.update_test(cpulse.uuid,
                                     {'state': new_state})
        self.assertEqual(new_state, res.state)

    def test_update_cloudpulse_test_uuid(self):
        cpulse = utils.create_cpulse_test()
        new_uuid = cloudpulse_utils.generate_uuid()
        self.assertRaises(exception.InvalidParameterValue,
                          self.dbapi.update_test, cpulse.uuid,
                          {'uuid': new_uuid})

    def test_update_cloudpulse_not_found(self):
        uuid = cloudpulse_utils.generate_uuid()
        new_state = 'running'
        self.assertRaises(exception.TestNotFound,
                          self.dbapi.update_test, uuid,
                          {'state': new_state})
