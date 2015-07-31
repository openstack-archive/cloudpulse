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
from cloudpulse.scenario import base
from cloudpulse.scenario.plugins.operator_tests import ansible_run
from cloudpulse.scenario.plugins.operator_tests import config
from oslo_config import cfg

TESTS_OPTS = [
    cfg.StrOpt('operator_setup_file',
               default='/etc/cloudpulse/operator.yaml',
               help='Setup File for the operator')
]

CONF = cfg.CONF

operator_test_group = cfg.OptGroup(name='operator_test',
                                   title='Options for the Operators')
CONF.register_group(operator_test_group)
CONF.register_opts(TESTS_OPTS, operator_test_group)


class operator_scenario(base.Scenario):

    def load(self):
        setup_file = cfg.CONF.operator_test.operator_setup_file
        self.ansirunner = ansible_run.AnsibleRunner()
        self.inventory = config.ConfigHelper(host_file=setup_file)
        self.host_list = self.inventory.get_host_list()
        self.host_ip_list = self.inventory.get_host_ip_list()
        self.remote_user = self.inventory.get_server_username()
        self.remote_pass = self.inventory.get_server_pass()
        self.percona_user = self.inventory.get_percona_username()
        self.percona_password = self.inventory.get_percona_pass()

    @base.scenario(admin_only=False, operator=True)
    def rabbitmq_check(self):
        # args = "systemctl | grep rabbitmq-server | grep running"
        self.load()
        args = "ps -ef | grep rabbitmq-server | grep -v grep"
        results, failed_hosts = self.ansirunner.\
            ansible_perform_operation(host_list=self.host_ip_list,
                                      remote_user=self.remote_user,
                                      remote_pass=self.remote_pass,
                                      module="shell",
                                      module_args=args)
        if results['status'] is 'PASS':
            return (200, "success", ['RabbitMQ-server Running'])
        else:
            return (404, "RabbitMQ-server not Running",
                    ['RabbitMQ-server not Running'])

    @base.scenario(admin_only=False, operator=True)
    def percona_check(self):
        self.load()
        args = r"mysql -u %s -p%s -e 'show databases;'| grep nova" % \
            (self.percona_user, self.percona_password)
        results, failed_hosts = self.ansirunner.\
            ansible_perform_operation(host_list=self.host_ip_list,
                                      remote_user=self.remote_user,
                                      remote_pass=self.remote_pass,
                                      module="shell",
                                      module_args=args)
        if results['status'] is 'PASS':
            return (200, "success", ['Percona Test Passed'])
        else:
            return (404, "Percona Test Failed: %s" % results, [])
