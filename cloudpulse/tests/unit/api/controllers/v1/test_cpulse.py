#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from cloudpulse import objects
from cloudpulse.tests.unit.db import base as db_base
from cloudpulse.tests.unit.db import utils

import mock
from mock import patch
from webtest.app import AppError


class TestCpulseController(db_base.DbTestCase):

    @patch('cloudpulse.conductor.api.API.test_create')
    def test_cpulse_create(self, mock_test_create):
        params = ('{"name": "nova_endpoint"}')
        response = self.app.post('/cpulse',
                                 params=params,
                                 content_type='application/json')
        self.assertEqual(response.status_int, 201)
        self.assertTrue(mock_test_create.called)

    def test_cpulse_create_name_not_given(self):
        params = ('{"name": ""}')
        self.assertRaises(AppError, self.app.post, '/cpulse',
                          params=params, content_type='application/json')

    @patch('cloudpulse.conductor.api.API.test_show')
    @patch('cloudpulse.objects.Cpulse.get_by_uuid')
    def test_cpulse_getone_by_uuid(self, mock_get_by_uuid, mock_test_show):
        cpulse = utils.get_cpulse_test()
        cpulse_obj = objects.Cpulse(self.context, **cpulse)
        mock_get_by_uuid.return_value = cpulse_obj
        uuid = cpulse.get('uuid')
        response = self.app.get('/cpulse/%s' % uuid)
        self.assertEqual(response.status_int, 200)

    @patch('cloudpulse.conductor.api.API.test_show')
    @patch('cloudpulse.objects.Cpulse.list')
    def test_cpulse_getall_tests(self, mock_test_list, mock_test_show):
        cpulse = utils.get_cpulse_test()
        cpulse_obj = [objects.Cpulse(self.context, **cpulse)]
        mock_test_list.return_value = cpulse_obj
        mock_test_show.return_value = cpulse_obj[0]
        response = self.app.get('/cpulse')
        self.assertEqual(response.status_int, 200)
        unittest_cpulses = response.json['cpulses']
        self.assertEqual(len(unittest_cpulses), 1)
        self.assertEqual(unittest_cpulses[0].get('uuid'),
                         cpulse['uuid'])

    @patch('cloudpulse.conductor.api.API.test_delete')
    def test_cpulse_delete_not_found(self, mock_test_delete):
        uuid = "123"
        self.assertRaises(AppError, self.app.delete, '/cpulse/%s' % uuid)

    @patch('cloudpulse.conductor.api.API.test_delete')
    @patch('cloudpulse.objects.Cpulse.get_by_uuid')
    def test_cpulse_delete_by_uuid(self, mock_get_by_uuid, mock_test_delete):
        cpulse = utils.get_cpulse_test()
        cpulse_obj = objects.Cpulse(self.context, **cpulse)
        mock_get_by_uuid.return_value = cpulse_obj
        uuid = cpulse.get('uuid')
        response = self.app.delete('/cpulse/%s' % uuid)
        mock_test_delete.assert_called_once_with(mock.ANY, uuid)
        self.assertEqual(response.status_int, 204)
