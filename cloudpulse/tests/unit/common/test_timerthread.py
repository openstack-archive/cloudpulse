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
from cloudpulse.common import timerthread
from cloudpulse import objects
from cloudpulse.tests.unit.db import base as db_base
from cloudpulse.tests.unit.db import utils

from mock import patch
import time


class Test_Cpulse_TimerThread(db_base.DbTestCase):

    @patch('cloudpulse.objects.Cpulse.list')
    def test_timerfunc_no_test(self, mock_test_list):
        timerthread.timerfunc()

    @patch('cloudpulse.TestManager.TestManager.TestManager.run')
    @patch('cloudpulse.objects.Cpulse.list')
    def test_timerfunc_list(self, mock_test_list, mock_TestManager_run):
        cpulse = utils.get_cpulse_test()
        cpulse_obj = [objects.Cpulse(self.context, **cpulse)]
        mock_test_list.return_value = cpulse_obj
        timerthread.timerfunc()
        time.sleep(1)
        self.assertTrue(mock_TestManager_run.not_called)

    @patch('cloudpulse.TestManager.TestManager.TestManager.run')
    @patch('cloudpulse.objects.Cpulse.list')
    def test_timerfunc_list_manual_test(self, mock_test_list,
                                        mock_TestManager_run):
        cpulse = utils.get_cpulse_test()
        cpulse['testtype'] = 'manual'
        cpulse_obj = [objects.Cpulse(self.context, **cpulse)]
        mock_test_list.return_value = cpulse_obj
        timerthread.timerfunc()
        time.sleep(1)
        mock_TestManager_run.assert_called_once_with(test=cpulse_obj[0])
