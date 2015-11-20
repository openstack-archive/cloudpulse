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


class Configs(object):

    # This file contains the details of cloudpulse server
    node_config_file = 'node_config.yaml'
    env_value = {}
    env_value['OS_USERNAME'] = 'admin'
    env_value['OS_TENANT_NAME'] = 'admin'
    env_value['OS_PASSWORD'] = 'cisco123'
    env_value['OS_AUTH_URL'] = 'http://172.29.74.99:5000/v2.0'
    env_value['OS_IDENTITY_API_VERSION'] = '2.0'
    env_value['OS_VOLUME_API_VERSION'] = '2'

    # Included for Periodic test case run
    # Provide the expected_testcase_run which depends on the
    # time interval & no of cases inside periodic test.
    expected_testcase_run = 3
    sleep_interval = 60 * 1
    input_periodic_test = {'neutron_endpoint': '20'}
    container_name = 'cloudpulse'

    test_case_name = 'security_keystone_admin_token_check'
    invalid_test_case_name = 'security_keystone_admin_token_check1'

    # All the testcases included here will check for success
    # run and show commands.
    # Include atleast one test case.
    all_test_cases = ['security_keystone_admin_token_check', 'rabbitmq_check']

    update_script = '/home/ubuntu/kiruba/test/functional/update_conf_file.py'
    revert_script = '/home/ubuntu/kiruba/test/functional/revert_conf_file.py'

    # Specify the location where the script file needs to be placed & executed
    tmp_loc = '/home/ubuntu/kiruba/test_123/'

    conf_file_path = '/etc/cloudpulse/cloudpulse.conf'

    # Below inputs are for endpoint verification.
    services_to_check = ['docker-keystone.service']
    endpoint_testcase = 'keystone_endpoint'
