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
from cloudpulse.operator.ansible.ansible_runner import ansible_runner
from cloudpulse.operator.ansible.openstack_node_info_reader import \
    openstack_node_info_reader
from cloudpulse.scenario import base
import json
from oslo_config import cfg
import re

TESTS_OPTS = [
    cfg.StrOpt('operator_setup_file',
               default='/etc/cloudpulse/openstack_config.yaml',
               help='Setup File for the operator'),
    cfg.BoolOpt('containerized',
                default=True,
                help='enable if the processes are running as containers'),
    cfg.StrOpt('rabbit_container',
               default='rabbitmq_v1',
               help='name of the rabitmq container'),
    cfg.StrOpt('galera_container',
               default='mariadb_v1',
               help='name of the galera cluster container'),

]

PERIODIC_TESTS_OPTS = [
    cfg.IntOpt('rabbitmq_check',
               default=0,
               help='The rabbitmq periodic check'),
    cfg.IntOpt('galera_check',
               default=0,
               help='The galera periodic check'),
    cfg.IntOpt('ceph_check',
               default=0,
               help='The ceph periodic check'),
    cfg.IntOpt('docker_check',
               default=0,
               help='The docker periodic check'),
    cfg.IntOpt('node_check',
               default=0,
               help='The Node Check peiodic check'),
    cfg.IntOpt('all_operator_tests',
               default=0,
               help='Run all operator tests')
]

CONF = cfg.CONF

operator_test_group = cfg.OptGroup(name='operator_test',
                                   title='Options for the Operators')
CONF.register_group(operator_test_group)
CONF.register_opts(TESTS_OPTS, operator_test_group)

periodic_test_group = cfg.OptGroup(name='periodic_tests',
                                   title='Periodic tests to be run')
CONF.register_opts(PERIODIC_TESTS_OPTS, periodic_test_group)


class operator_scenario(base.Scenario):

    def load(self):
        self.os_node_info_obj = openstack_node_info_reader(
            cfg.CONF.operator_test.operator_setup_file)
        openstack_node_list = self.os_node_info_obj.get_host_list()
        self.ans_runner = ansible_runner(openstack_node_list)
        inventory = self.ans_runner.init_ansible_inventory(openstack_node_list)
        self.ans_runner.set_ansible_inventory(inventory)

    @base.scenario(admin_only=False, operator=True)
    def rabbitmq_check(self):
        self.load()
        cmd = "rabbitmqctl cluster_status -q"

        is_containerized = cfg.CONF.operator_test.containerized
        if is_containerized:
            rabbit_container = cfg.CONF.operator_test.rabbit_container
            cmd = ("docker exec %s %s" % (rabbit_container, cmd))

        out = self.ans_runner.execute(cmd, roles=['controller'])
        res, output = self.ans_runner.validate_results(out)

        if res['status'] is 'PASS':
            node_status = res['contacted'][
                res['contacted'].keys()[0]]['stdout']
            node_status_string = node_status.replace('\n', '')

            nodes = []
            running = []
            mathobj = re.search(
                r'nodes,\[{disc,\[(.*?)\]', node_status_string, re.M | re.I)
            if mathobj:
                nodes = [x.rstrip(" ").lstrip(" ").rstrip("'").lstrip("'")
                         for x in mathobj.group(1).split(",")]

            mathobj = re.search(
                r'running_nodes,\[(.*?)\]}', node_status_string, re.M | re.I)

            if mathobj:
                running = [x.rstrip(" ").lstrip(" ").rstrip("'").lstrip("'")
                           for x in mathobj.group(1).split(",")]

            diffnodes = list(set(nodes) - set(running))
            if diffnodes:
                return(404, ("Failed Nodes : %s" %
                             str(diffnodes)))
            else:
                return (200, "Running Nodes : %s" % str(nodes),
                        ['RabbitMQ-server Running'])
        else:
            return (404, ("RabbitMQ-server test failed :%s" %
                          res['status_message']), [])

    @base.scenario(admin_only=False, operator=True)
    def galera_check(self):
        self.load()
        galera = self.os_node_info_obj.get_galera_details()

        cmd = ((r"mysql -u %s -p%s -e 'SHOW STATUS;'|grep "
                "wsrep_incoming_addresses") %
               (galera['username'], galera['password']))

        is_containerized = cfg.CONF.operator_test.containerized
        if is_containerized:
            galera_container = cfg.CONF.operator_test.galera_container
            cmd = ("docker exec %s %s" % (galera_container, cmd))

        out = self.ans_runner.execute(cmd, roles=['controller'])
        results, failed_hosts = self.ans_runner.validate_results(out)

        if results['status'] is 'PASS':
            galera_status = results['contacted'][
                results['contacted'].keys()[0]]['stdout']
            galera_status_string = galera_status.replace('\n', '')
            mathobj = re.search(r'wsrep_incoming_addresses\s+(.*?)$',
                                galera_status_string, re.M | re.I)
            nodes = mathobj.group(1)
            return (200, "Active Nodes : %s" % nodes,
                    ['Galera Cluster Test Passed'])
        else:
            return (404, ("Galera Cluster Test Failed: %s" %
                          results['status_message']), [])

    @base.scenario(admin_only=False, operator=True)
    def docker_check(self):
        self.load()
        cmd = "docker ps -aq --filter 'status=exited'"
        out = self.ans_runner.execute(cmd)

        results, failed_hosts = self.ans_runner.validate_results(out)
        if results['status'] is 'PASS':
            docker_failed = {key: results['contacted'][key]['stdout']
                             for key in results['contacted']
                             if results['contacted'][key]['stdout']}
            if docker_failed:
                docker_str = " ".join(["Containers failed in %s : %s" % (
                    key, docker_failed[key]) for key in docker_failed])
                return (404, docker_str, [])
            else:
                return (200, "All docker containers are up",
                        ['Docker container Test Passed'])
        else:
            return (404, ("Docker Check Failed: %s" %
                          results['status_message']), [])

    @base.scenario(admin_only=False, operator=True)
    def ceph_check(self):
        self.load()
        cmd = (r"ceph -f json status")
        out = self.ans_runner.execute(cmd, roles=['controller'])
        results, failed_hosts = self.ans_runner.validate_results(out)

        if results['status'] is 'PASS':
            ceph_status = results['contacted'][
                results['contacted'].keys()[0]]['stdout']
            ceph_status_string = ceph_status.replace('\n', '')
            ceph_json = json.loads(ceph_status_string)
            overall_status = ceph_json['health']['overall_status']
            num_of_osd = ceph_json['osdmap']['osdmap']['num_osds']
            num_up_osds = ceph_json['osdmap']['osdmap']['num_up_osds']
            if overall_status == 'HEALTH_OK':
                return (200, "Overall Status = %s, Cluster status = %s/%s" %
                        (overall_status, num_up_osds, num_of_osd))
            else:
                return (404, "Overall Status = %s, Cluster status = %s/%s" %
                        (overall_status, num_up_osds, num_of_osd))
        else:
            return (404, ("Ceph cluster Test Failed: %s" %
                          results['status_message']), [])

    @base.scenario(admin_only=False, operator=True)
    def node_check(self):
        self.load()
        out = self.ans_runner.ping()
        results, failed_hosts = self.ans_runner.validate_results(out)
        if results['status'] is 'PASS':
            return (200, "All nodes are up")
        else:
            msg = "Some nodes are not up"
            if failed_hosts:
                msg = "The following nodes are not up: %s" % str(
                    failed_hosts[0])
            return (404, msg)

    @base.scenario(admin_only=False, operator=True)
    def all_operator_tests(self):
        test_list = [func for func in dir(self) if base.Scenario.is_scenario(
            self, func) if not func.startswith(
            '__') if not func.startswith('all')]
        result = 200
        resultmsg = ""
        for func in test_list:
            funccall = getattr(self, func)
            try:
                funres = funccall()
            except Exception as e:
                funres = [404, str(e)]
            if funres[0] != 200:
                resultmsg += ("%s failed: %s\n" % (func, funres[1]))
                result = 404
        if not resultmsg:
            resultmsg = "All Tests passed"
        return (result, resultmsg)
