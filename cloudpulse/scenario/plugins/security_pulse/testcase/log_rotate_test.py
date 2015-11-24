# Copyright 2010-2011 OpenStack Foundation
# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
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

import cloudpulse
from cloudpulse.operator.ansible.ansible_runner import ansible_runner
import json
import os
import subprocess


class log_file_rotate_test(object):

    def perform_log_file_rotate_test(self, input_params):
        try:
            print ("Executing the test ", input_params.get('testcase_name'))
            file_info_dir = input_params['global_data']['file_info_dir']
            perform_on = input_params['perform_on']
            if perform_on is None or not perform_on:
                print ("Perform on should be mentioned either at test level \
                    or test case level")
                message = {
                    'message': 'Perform on should be mentioned either at \
                    test level or test case level'}
                return (404, json.dumps([message]), [])
            os_hostobj_list = input_params['os_host_list']
            base_dir = os.path.dirname(cloudpulse.__file__)
            flist = [base_dir +
                     "/scenario/plugins/security_pulse/testcase/" +
                     "remote_logrotate_check.py"]
            ans_runner = ansible_runner(os_hostobj_list)
            result = ans_runner.execute_cmd(
                "python " +
                file_info_dir +
                "remote_logrotate_check.py ",
                file_list=flist)
            Result = ans_runner.get_parsed_ansible_output(result)
            cmd = ['rm', '-rf', file_info_dir]
            subprocess.call(cmd)
            return Result
        except Exception:
            print (
                "Exception occured in executing" +
                " perform_log_file_rotate_test")
            message = {
                'message': 'Test case execution failed due to some exception'}
            return (404, json.dumps([message]), [])
