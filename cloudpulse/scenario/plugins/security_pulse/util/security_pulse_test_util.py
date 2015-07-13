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


def get_test_input_by_name(testcase_name, input_data):
    sec_test_lst = input_data['sec_test_lst']
    for test_obj in sec_test_lst:
        for test_case_obj in test_obj.get_security_testcase():
            if testcase_name == test_case_obj.get_test_name():
                input_params = test_case_obj.get_input_params()
                input_params['testcase_name'] = testcase_name
                if test_case_obj.get_perform_on() is not None:
                    input_params['perform_on'] = \
                        test_case_obj.get_perform_on()
                else:
                    input_params['perform_on'] = test_obj.get_perform_on()
                input_params['test_name'] = test_obj.get_test_name()
                input_params['global_data'] = input_data['global_data']
                return input_params
    return None
