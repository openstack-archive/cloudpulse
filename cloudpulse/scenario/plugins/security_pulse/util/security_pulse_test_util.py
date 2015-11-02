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

from cloudpulse.operator.ansible.openstack_node_info_reader import \
    openstack_node_info_reader
from cloudpulse.scenario.plugins.security_pulse.util.\
    security_pulse_test_input import security_test_input_reader
import os
from oslo_config import cfg

TESTS_OPTS = [
    cfg.StrOpt('testcase_input_file',
               default='',
               help='Security testcase input file'),
    cfg.StrOpt('testcase_setup_file',
               default='/etc/cloudpulse/openstack_config.yaml',
               help='setup file for security pulse test case'),
]

CONF = cfg.CONF

security_pulse_test_group = cfg.OptGroup(name='security_pulse_test',
                                         title='Security pulse test' +
                                         ' param input file')
CONF.register_group(security_pulse_test_group)
CONF.register_opts(TESTS_OPTS, security_pulse_test_group)


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


def get_all_openstack_node_list():
    openstack_node_list = []
    os_node_info_obj = openstack_node_info_reader(
        cfg.CONF.security_pulse_test.testcase_setup_file)
    openstack_node_list = os_node_info_obj.get_host_list()
    return openstack_node_list


def get_input_params(
        test_case_input_conf_file=None,
        test_input_file=None):
    input_params = {}
    try:
        if test_case_input_conf_file:
            input_reader = security_test_input_reader(
                test_case_input_conf_file)
            input_data = input_reader.process_security_input_file()
            input_params = get_test_input_by_name(test_input_file, input_data)
    except Exception:
        pass
    openstack_node_list = get_all_openstack_node_list()
    input_params['os_host_list'] = openstack_node_list
    return input_params


def check_for_valid_testcase_input_file():
    """Check for valid test case input yaml file

    if testcase i/p yaml file is not present return exception msg
    else return input yaml file name.

    """
    testcase_input_file = ""
    try:
        testcase_input_file =\
            cfg.CONF.security_pulse_test.testcase_input_file
    except Exception:
        msg = "Exception while reading the testcase input file"
        print (msg)
        return False, (404, msg, [])
    if not os.path.isfile(testcase_input_file):
        msg = 'Testcase input file %s not found' % (testcase_input_file)
        print (msg)
        return False, (404, msg, [])
    return True, testcase_input_file
