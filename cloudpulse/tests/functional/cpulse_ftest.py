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

import ansible.runner
import os
import sys
import test_config as config
import test_utils as utils
import time
import unittest
import uuid


class node_info_obj(object):

    def __init__(self, host, ip, user, role, name):
        self.host = host
        self.ip = ip
        self.user = user
        self.role = role
        self.name = name

    def getHost(self):
        return self.host

    def getIp(self):
        return self.ip

    def getUser(self):
        return self.user

    def getRole(self):
        return self.role

    def getName(self):
        return self.name


class node_info_reader(object):

    def __init__(self, host_file=None):
        if host_file is None:
            print ("Host file not passed. exit")
            sys.exit(0)
        self.host_file = utils.get_absolute_path_for_file(__file__, host_file)
        if not os.path.exists(self.host_file):
            print ("%s file does not exist" % self.host_file)
            return

        self.parsed_data = utils.create_parsed_yaml(self.host_file)

    def get_host_list(self):
        host_ip_list = []
        for key, data in self.parsed_data.items():
            hostname = key
            name = key
            ip = data.get('ip')
            user = data.get('user')
            role = data.get('role')
            node = node_info_obj(hostname, ip, user, role, name)
            host_ip_list.append(node)
        return host_ip_list


class AnsibleRunner(object):

    def __init__(self,
                 host_list=None,
                 remote_user=None,
                 sudo=True):
        # AnsibleRunner init.
        self.host_list = host_list
        self.sudo = sudo

    def get_validated_data(self, results, stdout=True, stderr=False):
        # print ("\n\nInside get_validated_data", results)
        output = ''
        ###################################################
        # First validation is to make sure connectivity to
        # all the hosts was ok.
        ###################################################
        if results['dark']:
            output = ''

        ##################################################
        # Now look for status 'failed'
        ##################################################
        for node in results['contacted'].keys():
            if 'failed' in results['contacted'][node]:
                if results['contacted'][node]['failed'] is True:
                    output = ''

        #################################################
        # Check for the return code 'rc' for each host.
        #################################################
        for node in results['contacted'].keys():
            info = results['contacted'][node]
            if stdout:
                op = info.get('stdout')
            else:
                op = info.get('stderr')
            output = op
        return output

    def ansible_perform_operation(self,
                                  host_list=None,
                                  remote_user=None,
                                  module=None,
                                  complex_args=None,
                                  module_args='',
                                  environment=None,
                                  check=False,
                                  forks=2,
                                  stderr=None,
                                  stdout=None):
        # Perform any ansible operation.
        runner = ansible.runner.Runner(
            module_name=module,
            host_list=host_list,
            remote_user=remote_user,
            module_args=module_args,
            complex_args=complex_args,
            environment=environment,
            check=check,
            forks=forks)

        results = runner.run()
        res = self.get_validated_data(results, stdout, stderr)
        return res


class FunctionalTestMethods(unittest.TestCase):

    ansirunner = AnsibleRunner()
    config = config.Configs()
    node_config_file_name = config.node_config_file
    node_reader = node_info_reader(node_config_file_name)
    node_list = node_reader.get_host_list()
    env_value = config.env_value
    TEST_CASE_NAME = config.test_case_name
    INVALID_TEST_CASE_NAME = config.invalid_test_case_name
    TEST_CASES = config.all_test_cases

    # expected_testcase_run = config.expected_testcase_run
    # sleep_interval = config.sleep_interval
    # input_periodic_test = config.input_periodic_test
    # container_name = config.container_name

    # update_script_file = config.update_script
    # revert_script_file = config.revert_script
    # tmp_loc = config.tmp_loc
    # conf_file_path = config.conf_file_path

    # endpoint testcase validation check
    # services_to_check = config.services_to_check
    # endpoint_testcase = config.endpoint_testcase

    @classmethod
    def setUpClass(cls):
        # set_env_variables(cls.env_value)
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def get_node_details(self, node_info):
        self.host_list = node_info.getIp()
        self.remote_user = node_info.getUser()
        self.host = node_info.getHost()
        self.role = node_info.getRole()

    def reset_node_details(self):
        self.host_list = None
        self.remote_user = None
        self.host = None
        self.role = None

    # Check for test run with invalid test case name with credentials
    def test_invalid_test_case_run(self):
        opt = utils.form_cli_env_params(self.env_value)
        cmd = "%s run %s" % (opt, self.INVALID_TEST_CASE_NAME)
        run_cmd = utils.form_cmd(cmd)
        for node in self.node_list:
            self.get_node_details(node)
            res = self.ansirunner.ansible_perform_operation(
                host_list=[self.host_list],
                remote_user=self.remote_user,
                module="shell",
                module_args=run_cmd,
                stdout=False,
                stderr=True)
            check = self.INVALID_TEST_CASE_NAME + ' is invalid'
            self.assertIn(check, res)
            self.reset_node_details()

    # Check for test run with valid test case name with credentials
    def test_valid_test_case_run_and_delete(self):
        opt = utils.form_cli_env_params(self.env_value)
        cmd = "%s run %s" % (opt, self.TEST_CASE_NAME)
        run_cmd = utils.form_cmd(cmd)
        for node in self.node_list:
            self.get_node_details(node)
            res = self.ansirunner.ansible_perform_operation(
                host_list=[self.host_list],
                remote_user=self.remote_user,
                module="shell",
                module_args=run_cmd,
                stdout=True,
                stderr=False)
            result = utils.parse_run_cmd_result(res)
            self.assertIn('Pass', result)
            # Try deleting the test case
            del_uuid = utils.get_uuid(res)
            cmd = "%s delete %s" % (opt, del_uuid)
            delete_cmd = utils.form_cmd(cmd)
            res = self.ansirunner.ansible_perform_operation(
                host_list=[self.host_list],
                remote_user=self.remote_user,
                module="shell",
                module_args=delete_cmd,
                stdout=True,
                stderr=False)
            self.assertIn('', res)
            self.reset_node_details()

    # Check for test run with invalid test case name with env variable
    def test_invalid_test_case_run_with_env(self):
        cmd = "run %s" % (self.INVALID_TEST_CASE_NAME)
        run_cmd = utils.form_cmd(cmd)
        for node in self.node_list:
            self.get_node_details(node)
            res = self.ansirunner.ansible_perform_operation(
                host_list=[self.host_list],
                remote_user=self.remote_user,
                module="shell",
                module_args=run_cmd,
                environment=self.env_value,
                stdout=False,
                stderr=True)
            check = self.INVALID_TEST_CASE_NAME + ' is invalid'
            self.assertIn(check, res)
            self.reset_node_details()

    # Check for run & show command using credentials
    def test_run_and_show_result(self):
        opt = utils.form_cli_env_params(self.env_value)
        cmd = "%s run %s" % (opt, self.TEST_CASE_NAME)
        run_cmd = utils.form_cmd(cmd)
        for node in self.node_list:
            self.get_node_details(node)
            res = self.ansirunner.ansible_perform_operation(
                host_list=[self.host_list],
                remote_user=self.remote_user,
                module="shell",
                module_args=run_cmd,
                stdout=True,
                stderr=False)
            result = utils.parse_run_cmd_result(res)
            self.assertIn('Pass', result)
            if res:
                # Wait till the run completes and then execute show cmd
                time.sleep(5)
                uuid = utils.get_uuid(res)
                cmd = "%s show %s" % (opt, uuid)
                show_cmd = utils.form_cmd(cmd)
                res = self.ansirunner.ansible_perform_operation(
                    host_list=[self.host_list],
                    remote_user=self.remote_user,
                    module="shell",
                    module_args=show_cmd,
                    stdout=True,
                    stderr=False)
                result = utils.parse_show_cmd_result(res, uuid)
                self.assertEqual('Pass', result)
            self.reset_node_details()

    # Check for run & show command using credentials
    def test_multiple_run_and_show(self):
        opt = utils.form_cli_env_params(self.env_value)
        for case in self.TEST_CASES:
            cmd = "%s run %s" % (opt, case)
            run_cmd = utils.form_cmd(cmd)
            for node in self.node_list:
                self.get_node_details(node)
                res = self.ansirunner.ansible_perform_operation(
                    host_list=[self.host_list],
                    remote_user=self.remote_user,
                    module="shell",
                    module_args=run_cmd,
                    stdout=True,
                    stderr=False)
                if res:
                    uuid = utils.get_uuid(res)
                    cmd = "%s show %s" % (opt, uuid)
                    show_cmd = utils.form_cmd(cmd)
                    res = self.ansirunner.ansible_perform_operation(
                        host_list=[self.host_list],
                        remote_user=self.remote_user,
                        module="shell",
                        module_args=show_cmd,
                        stdout=True,
                        stderr=False)
                    # Wait till the run completes and then execute show cmd
                    time.sleep(5)
                    result = utils.parse_show_cmd_result(res, uuid)
                    self.assertEqual('Pass', result)
                self.reset_node_details()

    # Check for result command is working with credentials
    def test_result_cmd(self):
        opt = utils.form_cli_env_params(self.env_value)
        # result_cmd = "cloudpulse %s result"%(opt)
        cmd = "%s result" % (opt)
        result_cmd = utils.form_cmd(cmd)
        for node in self.node_list:
            self.get_node_details(node)
            res = self.ansirunner.ansible_perform_operation(
                host_list=[self.host_list],
                remote_user=self.remote_user,
                module="shell",
                module_args=result_cmd,
                stdout=True,
                stderr=False)
            result = utils.parse_result_cmd_result(res)
            self.assertIn('Pass', result)
            self.reset_node_details()

    # Check for delete command with invalid uuid is working with credentials
    def test_delete_cmd_with_invalid_uuid(self):
        opt = utils.form_cli_env_params(self.env_value)
        del_uuid = str(uuid.uuid4())
        cmd = "%s delete %s" % (opt, del_uuid)
        delete_cmd = utils.form_cmd(cmd)
        for node in self.node_list:
            self.get_node_details(node)
            res = self.ansirunner.ansible_perform_operation(
                host_list=[self.host_list],
                remote_user=self.remote_user,
                module="shell",
                module_args=delete_cmd,
                stdout=True,
                stderr=False)
            check = 'Test %s could not be found' % (del_uuid)
            self.assertIn(check, res)
            self.reset_node_details()

    def test_with_invalid_user(self):
        opt = utils.form_cli_env_params(self.env_value, invalid_uname=True)
        cmd = '%s result ' % (opt)
        result_cmd = utils.form_cmd(cmd)
        for node in self.node_list:
            self.get_node_details(node)
            res = self.ansirunner.ansible_perform_operation(
                host_list=[self.host_list],
                remote_user=self.remote_user,
                module="shell",
                module_args=result_cmd,
                stdout=False,
                stderr=True)
            check = 'Could not find user:'
            self.assertIn(check, res)
            self.reset_node_details()

    def test_with_invalid_password(self):
        opt = utils.form_cli_env_params(self.env_value, invalid_pwd=True)
        cmd = '--debug %s result ' % (opt)
        result_cmd = utils.form_cmd(cmd)
        for node in self.node_list:
            self.get_node_details(node)
            pwd_test = self.ansirunner.ansible_perform_operation(
                host_list=[self.host_list],
                remote_user=self.remote_user,
                module="shell",
                module_args=result_cmd,
                stdout=False,
                stderr=True)
            check = 'Invalid user / password'
            self.assertIn(check, pwd_test)
            self.reset_node_details()

    def test_with_invalid_tenant(self):
        opt = utils.form_cli_env_params(self.env_value, invalid_tenant=True)
        cmd = '--debug %s result ' % (opt)
        result_cmd = utils.form_cmd(cmd)
        for node in self.node_list:
            self.get_node_details(node)
            tenant_test = self.ansirunner.ansible_perform_operation(
                host_list=[self.host_list],
                remote_user=self.remote_user,
                module="shell",
                module_args=result_cmd,
                stdout=False,
                stderr=True)
            check = 'Could not find project'
            self.assertIn(check, tenant_test)
            self.reset_node_details()

    def test_with_invalid_auth(self):
        opt = utils.form_cli_env_params(self.env_value, invalid_auth=True)
        cmd = '--debug %s result ' % (opt)
        result_cmd = utils.form_cmd(cmd)
        for node in self.node_list:
            self.get_node_details(node)
            res = self.ansirunner.ansible_perform_operation(
                host_list=[self.host_list],
                remote_user=self.remote_user,
                module="shell",
                module_args=result_cmd,
                stdout=False,
                stderr=True)
            check = 'Authorization Failed'
            self.assertIn(check, res)
            self.reset_node_details()


if __name__ == '__main__':
    unittest.main()
