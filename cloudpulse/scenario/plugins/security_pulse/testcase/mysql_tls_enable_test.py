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


class mysql_tls_enablement_test(object):

    def perform_mysql_tls_enablement_test(self, input_params):
        try:
            file_info_dir = input_params['global_data']['file_info_dir']
            is_containerized = input_params['global_data']['is_containerized']
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
            flist = [base_dir + "/scenario/plugins/security_pulse" +
                     "/testcase/remote_mysql_tls_enablement_check.py"]
            ans_runner = ansible_runner(os_hostobj_list)
            container_name = None
            if is_containerized:
                container_name = input_params['input']['container_name']
            result = ans_runner.execute_cmd(
                "python " +
                file_info_dir +
                "remote_mysql_tls_enablement_check.py ",
                file_list=flist, container_name=container_name)
            Result = ans_runner.get_parsed_ansible_output(result)
            subprocess.call(['rm', '-rf', file_info_dir + 'output'])
            return Result
        except Exception as msg:
            print (
                "Exception while executing perform_mysql_tls_enablement_test")
            print (msg)
            message = {
                'message': 'Test case execution failed due to some exception'}
            return (404, json.dumps([message]), [])
