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
    env_value['OS_USERNAME'] = 'root'
    env_value['OS_TENANT_NAME'] = 'root'
    env_value['OS_PASSWORD'] = 'password'
    env_value['OS_AUTH_URL'] = 'http://127.0.0.1:5000/v2.0'
    env_value['OS_IDENTITY_API_VERSION'] = '2.0'
    env_value['OS_VOLUME_API_VERSION'] = '2'

    test_case_name = 'rabbitmq_check'
    invalid_test_case_name = 'rabbitmq_check_test'

    # All the testcases included here will check for success
    # run and show commands.
    # Include atleast one test case.
    all_test_cases = ['rabbitmq_check']
