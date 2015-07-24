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
from cloudpulse.common import exception
from cloudpulse.common import utils as cloudpulse_utils
from cloudpulse import objects
from cloudpulse.tests.unit.db import base
from cloudpulse.tests.unit.db import utils

import mock


class TestCpulseObject(base.DbTestCase):

    def setUp(self):
        super(TestCpulseObject, self).setUp()
        self.cpulsetest = utils.get_cpulse_test()

    def test_get_with_id(self):
        cpulse_id = self.cpulsetest['id']
        with mock.patch.object(self.dbapi, 'get_test_by_id',
                               autospec=True) as mock_get_test:
            mock_get_test.return_value = self.cpulsetest
            cpulse = objects.Cpulse.get(self.context,
                                        cpulse_id)
            mock_get_test.assert_called_once_with(self.context,
                                                  cpulse_id)
            self.assertEqual(self.context, cpulse._context)

    def test_get_with_uuid(self):
        cpulse_id = self.cpulsetest['uuid']
        with mock.patch.object(self.dbapi, 'get_test_by_uuid',
                               autospec=True) as mock_get_test:
            mock_get_test.return_value = self.cpulsetest
            cpulse = objects.Cpulse.get(self.context,
                                        cpulse_id)
            mock_get_test.assert_called_once_with(self.context,
                                                  cpulse_id)
            self.assertEqual(self.context, cpulse._context)

    def test_get_exception(self):
        cpulse_id = "cpulsetest"
        self.assertRaises(exception.InvalidIdentity, objects.Cpulse.get,
                          self.context, cpulse_id)

    def test_get_by_uuid(self):
        cpulse_id = self.cpulsetest['uuid']
        with mock.patch.object(self.dbapi, 'get_test_by_uuid',
                               autospec=True) as mock_get_test:
            mock_get_test.return_value = self.cpulsetest
            cpulse = objects.Cpulse.get_by_uuid(self.context,
                                                cpulse_id)
            mock_get_test.assert_called_once_with(self.context,
                                                  cpulse_id)
            self.assertEqual(self.context, cpulse._context)

    def test_get_by_name(self):
        cpulse_name = self.cpulsetest['name']
        with mock.patch.object(self.dbapi, 'get_test_by_name',
                               autospec=True) as mock_get_test:
            mock_get_test.return_value = self.cpulsetest
            cpulse = objects.Cpulse.get_by_name(self.context,
                                                cpulse_name)
            mock_get_test.assert_called_once_with(self.context,
                                                  cpulse_name)
            self.assertEqual(self.context, cpulse._context)

    def test_get_by_id(self):
        cpulse_id = self.cpulsetest['id']
        with mock.patch.object(self.dbapi, 'get_test_by_id',
                               autospec=True) as mock_get_test:
            mock_get_test.return_value = self.cpulsetest
            cpulse = objects.Cpulse.get_by_id(self.context,
                                              cpulse_id)
            mock_get_test.assert_called_once_with(self.context,
                                                  cpulse_id)
            self.assertEqual(self.context, cpulse._context)

    def test_list(self):
        with mock.patch.object(self.dbapi, 'get_test_list',
                               autospec=True) as mock_get_list:
            mock_get_list.return_value = [self.cpulsetest]
            cpulse = objects.Cpulse.list(self.context)
            self.assertEqual(mock_get_list.call_count, 1)
            self.assertEqual(len(cpulse), 1)
            self.assertIsInstance(cpulse[0], objects.Cpulse)
            self.assertEqual(self.context, cpulse[0]._context)

    def test_cpulse_create(self):
        with mock.patch.object(self.dbapi, 'create_test',
                               autospec=True) as mock_create_test:
            mock_create_test.return_value = self.cpulsetest
            cpulse = objects.Cpulse(self.context, **self.cpulsetest)
            cpulse.create()
            mock_create_test.assert_called_once_with(self.cpulsetest)
            self.assertEqual(self.context, cpulse._context)

    def test_cpulse_destroy(self):
        uuid = self.cpulsetest['uuid']
        with mock.patch.object(self.dbapi, 'get_test_by_uuid',
                               autospec=True) as mock_get_cpulse:
            mock_get_cpulse.return_value = self.cpulsetest
            with mock.patch.object(self.dbapi, 'destroy_test',
                                   autospec=True) as mock_destroy_cpulse:
                cpulse = objects.Cpulse.get_by_uuid(self.context, uuid)
                cpulse.destroy()
                mock_get_cpulse.assert_called_once_with(self.context, uuid)
                mock_destroy_cpulse.assert_called_once_with(uuid)
                self.assertEqual(self.context, cpulse._context)

    def test_save(self):
        uuid = self.cpulsetest['uuid']
        with mock.patch.object(self.dbapi, 'get_test_by_uuid',
                               autospec=True) as mock_get_cpulse:
            mock_get_cpulse.return_value = self.cpulsetest
            with mock.patch.object(self.dbapi, 'update_test',
                                   autospec=True) as mock_update_cpulse:
                cpulse = objects.Cpulse.get_by_uuid(self.context, uuid)
                cpulse.state = 'running'
                cpulse.save()

                mock_get_cpulse.assert_called_once_with(self.context, uuid)
                mock_update_cpulse.assert_called_once_with(
                    uuid, {'state': 'running'})
                self.assertEqual(self.context, cpulse._context)

    def test_refresh(self):
        uuid = self.cpulsetest['uuid']
        new_uuid = cloudpulse_utils.generate_uuid()
        returns = [dict(self.cpulsetest, uuid=uuid),
                   dict(self.cpulsetest, uuid=new_uuid)]
        expected = [mock.call(self.context, uuid),
                    mock.call(self.context, uuid)]
        with mock.patch.object(self.dbapi, 'get_test_by_uuid',
                               side_effect=returns,
                               autospec=True) as mock_get_cpulse:
            cpulse = objects.Cpulse.get_by_uuid(self.context, uuid)
            self.assertEqual(uuid, cpulse.uuid)
            cpulse.refresh()
            self.assertEqual(new_uuid, cpulse.uuid)
            self.assertEqual(expected, mock_get_cpulse.call_args_list)
            self.assertEqual(self.context, cpulse._context)
