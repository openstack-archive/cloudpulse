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
# from cloudpulse.operator.ansible.openstack_node import openstack_node_obj
from cloudpulse.operator.ansible.openstack_node_info_reader import \
    openstack_node_info_reader
from cloudpulse.scenario import base
from cloudpulse.scenario.plugins.security_pulse.testcase.tls_enable_test \
    import tls_enablement_test
from cloudpulse.scenario.plugins.security_pulse.testcase.\
    ks_admin_token_check import ks_admin_token_check
from cloudpulse.scenario.plugins.security_pulse.util.\
    security_pulse_test_input import security_test_input_reader
from cloudpulse.scenario.plugins.security_pulse.util import \
    security_pulse_test_util
import os
from oslo_config import cfg

TESTS_OPTS = [
    cfg.StrOpt('testcase_input_file',
               default='',
               help='Security testcase input file')
]

CONF = cfg.CONF

security_pulse_test_group = cfg.OptGroup(name='security_pulse_test',
                                         title='Security pulse test' +
                                         ' param input file')
CONF.register_group(security_pulse_test_group)
CONF.register_opts(TESTS_OPTS, security_pulse_test_group)


class security_common_test(base.Scenario):

    def security_keystone_tls_enablement_check(self, *args, **kwargs):
        testcase_input_file = ""
        try:
            testcase_input_file =\
                cfg.CONF.security_pulse_test.testcase_input_file
        except Exception as e:
            print ("Exception while reading the testcase input file")
            return (404, e.message, [])
        if not os.path.isfile(testcase_input_file):
            print ("Security Testcase input file not found")
            return (404, "Security Testcase input file not found", [])
        # print testcase_input_file
        base_dir = os.path.dirname(cloudpulse.__file__)
        input_reader = security_test_input_reader(testcase_input_file)
        input_data = input_reader.process_security_input_file()
        input_params = security_pulse_test_util.\
            get_test_input_by_name("tls_enablement_check", input_data)
        os_node_info_obj = \
            openstack_node_info_reader(base_dir +
                                       "/scenario/plugins/security_pulse/" +
                                       "config/openstack_config.yaml")
        openstack_node_list = os_node_info_obj.get_host_list()
        input_params['os_host_list'] = openstack_node_list
        # print input_params
        tls_test = tls_enablement_test()
        result = tls_test.perform_tls_enablement_test(input_params)
        if not result:
            return (404, "No result from test execution", [])
        # print result
        if result.startswith("Fail"):
            return (404, result, [])
        else:
            return (200, result, [])

    def security_keystone_admin_token_check(self, *args, **kwargs):
        testcase_input_file = ""
        try:
            testcase_input_file =\
                cfg.CONF.security_pulse_test.testcase_input_file
        except Exception as e:
            print ("Exception while reading the testcase input file")
            return (404, e.message, [])
        if not os.path.isfile(testcase_input_file):
            return (404, "Security Testcase input file not found", [])
        base_dir = os.path.dirname(cloudpulse.__file__)
        input_reader = security_test_input_reader(testcase_input_file)
        input_data = input_reader.process_security_input_file()
        input_params = security_pulse_test_util.\
            get_test_input_by_name("ks_admin_token_check", input_data)
        os_node_info_obj = \
            openstack_node_info_reader(base_dir +
                                       "/scenario/plugins/security_pulse/" +
                                       "config/openstack_config.yaml")
        openstack_node_list = os_node_info_obj.get_host_list()
        input_params['os_host_list'] = openstack_node_list
        # print input_params
        ks_test = ks_admin_token_check()
        result = ks_test.perform_ks_admin_token_check_test(input_params)
        if not result:
            return (404, "No result from test execution", [])
        # print result
        test_status = None
        data = ""
        for r in result:
            if test_status is None or r[2].startswith("Fail"):
                test_status = "fail"
            elif test_status is None:
                test_status = "success"
            data = data + r[0] + " -> " + r[1] + " -> " + r[2] + "\n"
        if test_status == "fail":
            return (404, data, [])
        else:
            return (200, data, [])

if __name__ == '__main__':
    sct = security_common_test()
    sct.security_tls_enablement_check()
