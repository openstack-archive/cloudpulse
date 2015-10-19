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
from cloudpulse.scenario.plugins.security_pulse.testcase.mysql_tls_enable_test\
    import mysql_tls_enablement_test
from cloudpulse.scenario.plugins.security_pulse.util.\
    security_pulse_test_input import security_test_input_reader
from cloudpulse.scenario.plugins.security_pulse.util import \
    security_pulse_test_util
import json
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


class security_mysql_test(base.Scenario):

    def security_mysql_tsl_enable_check(self, *args, **kwargs):
        testcase_input_file = ""
        try:
            testcase_input_file =\
                cfg.CONF.security_pulse_test.testcase_input_file
        except Exception as e:
            print ("Exception while reading the testcase input file")
            return (404, json.dumps([{'Message': e.message}]), [])
        if not os.path.isfile(testcase_input_file):
            print ("Security mysql Testcase input file not found")
            msg = {'Message': "Security mysql Testcase input file not found"}
            return (404, json.dumps([msg]), [])
        base_dir = os.path.dirname(cloudpulse.__file__)
        input_reader = security_test_input_reader(testcase_input_file)
        input_data = input_reader.process_security_input_file()
        input_params = security_pulse_test_util.\
            get_test_input_by_name("mysql_tls_enablement_test", input_data)
        # os_node_info_obj = \
        #     openstack_node_info_reader(base_dir +
        #                                "/scenario/plugins/security_pulse/" +
        #                                "config/openstack_config.yaml")
        os_node_info_obj = openstack_node_info_reader(
            cfg.CONF.security_pulse_test.testcase_setup_file)
        openstack_node_list = os_node_info_obj.get_host_list()
        input_params['os_host_list'] = openstack_node_list
        mysql_common_test = mysql_tls_enablement_test()
        result = \
            mysql_common_test.perform_mysql_tls_enablement_test(input_params)
        print ("result from security_mysql_tsl_enable_check")
        print (result)
        return result


if __name__ == '__main__':
    sct = security_mysql_test()
    sct.security_mysql_tsl_enable_check()
