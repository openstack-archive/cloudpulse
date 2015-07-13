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

from __future__ import print_function
import cloudpulse
from cloudpulse.operator.ansible.ansible_runner import ansible_runner
import os

TMP_LOCATION = "/tmp/sec_hc/"


class ks_admin_token_check(object):

    def perform_ks_admin_token_check_test(self, input_params):
        print ("Executing the test ", input_params.get('testcase_name'))
        file_info_dir = input_params['global_data']['file_info_dir']
        perform_on = input_params['perform_on']
        if perform_on is None or not perform_on:
            print ("Perform on should be mentioned either at \
                    test level or test case level")
            return
        os_hostobj_list = input_params['os_host_list']
        base_dir = os.path.dirname(cloudpulse.__file__)
        flist = [base_dir +
                 "/scenario/plugins/security_pulse/testcase/" +
                 "keystone_admin_token_check.py"]
        ans_runner = ansible_runner(os_hostobj_list)
        ans_runner.execute_cmd("python " + TMP_LOCATION +
                               "keystone_admin_token_check.py " +
                               TMP_LOCATION, file_list=flist)
        result = ans_runner.get_results()
        if not result:
            return result
        result_row = []
        for key in result.keys():
            obj = eval(result[key])
            for r in obj:
                result = r.split(" - ")
                result_row.append([result[0], result[1], result[2]])
        os.system('rm -rf ' + file_info_dir + 'output')
        return result_row
