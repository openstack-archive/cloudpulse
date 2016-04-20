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
from cloudpulse import objects
from cloudpulse.scenario import base
from cloudpulse.scenario.plugins.security_pulse.testcase.file_check_test\
    import SecurityFileCheck
from cloudpulse.scenario.plugins.security_pulse.testcase.\
    ks_admin_token_check import ks_admin_token_check
from cloudpulse.scenario.plugins.security_pulse.testcase.log_rotate_test \
    import log_file_rotate_test
from cloudpulse.scenario.plugins.security_pulse.testcase.logfile_mode_test\
    import log_file_mode_check_test
"""
from cloudpulse.scenario.plugins.security_pulse.testcase.mysql_db_test\
    import mysql_db_test
"""
from cloudpulse.scenario.plugins.security_pulse.testcase.mysql_tls_enable_test\
    import mysql_tls_enablement_test
from cloudpulse.scenario.plugins.security_pulse.testcase.\
    password_encryption_test import password_encryption_check
from cloudpulse.scenario.plugins.security_pulse.testcase.tls_enable_test \
    import tls_enablement_test
from cloudpulse.scenario.plugins.security_pulse.util import \
    security_pulse_test_util as utils
import json
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


class security_pulse_scenario(base.Scenario):

    @base.scenario(admin_only=False, operator=False)
    def password_encryption_check(self, *args, **kwargs):
        status, result = utils.check_for_valid_testcase_input_file()
        if status:
            testcase_input_file = result
        else:
            return result
        input_params = utils.get_input_params(
            testcase_input_file, "password_encryption_check")
        pwd_test = password_encryption_check()
        result = pwd_test.perform_password_encryption_test(input_params)
        return result

    @base.scenario(admin_only=False, operator=False)
    def keystone_tls_check(self, *args, **kwargs):
        status, result = utils.check_for_valid_testcase_input_file()
        if status:
            testcase_input_file = result
        else:
            return result
        input_params = utils.get_input_params(
            testcase_input_file, "tls_enablement_check")
        test = tls_enablement_test()
        result = test.perform_tls_enablement_test(input_params)
        return result

    @base.scenario(admin_only=False, operator=False)
    def keystone_admin_token_check(self, *args, **kwargs):
        status, result = utils.check_for_valid_testcase_input_file()
        if status:
            testcase_input_file = result
        else:
            return result
        input_params = utils.get_input_params(
            testcase_input_file, "ks_admin_token_check")
        test = ks_admin_token_check()
        result = test.perform_ks_admin_token_check_test(input_params)
        return result

    @base.scenario(admin_only=False, operator=False)
    def file_comparision_check(self, *args, **kwargs):
        status, result = utils.check_for_valid_testcase_input_file()
        if status:
            testcase_input_file = result
        else:
            return result
        input_params = utils.get_input_params(
            testcase_input_file, "filepermission")
        test = SecurityFileCheck()
        result = test.perform_file_permission_check(input_params)
        return result

    @base.scenario(admin_only=False, operator=False)
    def logfile_mode_check(self, *args, **kwargs):
        status, result = utils.check_for_valid_testcase_input_file()
        if status:
            testcase_input_file = result
        else:
            return result
        input_params = utils.get_input_params(
            testcase_input_file, "logfile_mode_check")
        test = log_file_mode_check_test()
        result = test.perform_log_file_mode_test(input_params)
        return result

    @base.scenario(admin_only=False, operator=False)
    def logfile_rotate_check(self, *args, **kwargs):
        status, result = utils.check_for_valid_testcase_input_file()
        if status:
            testcase_input_file = result
        else:
            return result
        input_params = utils.get_input_params(
            testcase_input_file, "logrotate_cfg_check")
        test = log_file_rotate_test()
        result = test.perform_log_file_rotate_test(input_params)
        return result

    @base.scenario(admin_only=False, operator=False)
    def mysql_tsl_check(self, *args, **kwargs):
        status, result = utils.check_for_valid_testcase_input_file()
        if status:
            testcase_input_file = result
        else:
            return result
        input_params = utils.get_input_params(
            testcase_input_file, "mysql_tls_enablement_test")
        test = mysql_tls_enablement_test()
        result = test.perform_mysql_tls_enablement_test(input_params)
        return result

    # def mysql_db_check(self, *args, **kwargs):
    #     status, result = utils.check_for_valid_testcase_input_file()
    #     if status:
    #         testcase_input_file = result
    #     else:
    #         return result
    #     input_params = utils.get_input_params(
    #         testcase_input_file, "mysql_db_test")
    #     test = mysql_db_test()
    #     result = test.perform_mysql_db_test(input_params)
    #     print ("result from mysql_db_check")
    #     print (result)
    #     return result

    def verbose(self, *args, **kwargs):
        context = kwargs['context']
        cpulse_id = kwargs['uuid']
        cpulse = objects.Cpulse.get(context, cpulse_id)
        result_string = cpulse['result']
        final_string = ""
        for line in result_string.split("\n"):
            final_string += line.ljust(40)
        result_final = json.loads(final_string)
        result_final2 = {"verbose": result_final}
        return result_final2

if __name__ == '__main__':
    spt = security_pulse_scenario()
    spt.password_encryption_check()
