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
from cloudpulse.openstack.api.nova_api import NovaHealth
from cloudpulse.operator.ansible.openstack_node_info_reader import \
    openstack_node_info_reader

from cloudpulse.scenario import base
import errno
import os
from oslo_config import cfg
from oslo_utils import importutils
import re
import shlex
import simplejson
from subprocess import PIPE
from subprocess import Popen

TESTS_OPTS = [
    cfg.StrOpt('operator_setup_file',
               default='/etc/cloudpulse/openstack_config.yaml',
               help='Setup File for the operator'),
    cfg.BoolOpt('containerized',
                default=True,
                help='enable if the processes are running as containers'),
    cfg.StrOpt('rabbit_container',
               default='rabbitmq',
               help='name of the rabitmq container'),
    cfg.StrOpt('galera_container',
               default='mariadb',
               help='name of the galera cluster container'),
    cfg.StrOpt('ceph_container',
               default='ceph',
               help='name of the ceph cluster container'),
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

cfg.CONF.import_opt('auth_uri', 'keystonemiddleware.auth_token',
                    group='keystone_authtoken')


def execute(command):

    try:
        command = shlex.split(command)
        stdout = None
        stderr = None
        p = Popen(command, shell=False, stdout=PIPE,
                  stderr=PIPE,
                  bufsize=-1, env=os.environ, close_fds=True)
        stdout, stderr = p.communicate()
    except OSError as e:
        if e.errno == errno.ENOENT:
            return {'status': 127, 'output': ""}
        else:
            return {'status': 126, 'output': ""}

    if p.returncode == 126 or p.returncode == 127:
        stdout = str(b"")
    return {'status': p.returncode, 'output': stdout}


def get_container_name(name):
    cmd = "ansible -o all  -i 127.0.0.1, -a 'docker ps' -u root"
    op = execute(cmd)
    if op['status']:
        return None
    dockerps = op['output'].split('\\n')
    for line in dockerps:
        if name in line:
            linear = line.split()
            return linear[len(linear) - 1].strip('\n')
    return None


class operator_scenario(base.Scenario):
    def _get_nova_hypervior_list(self):
        importutils.import_module('keystonemiddleware.auth_token')
        creds = {}
        creds['username'] = cfg.CONF.keystone_authtoken.username
        creds['project_id'] = cfg.CONF.keystone_authtoken.project_name
        creds['api_key'] = cfg.CONF.keystone_authtoken.password
        creds['auth_url'] = cfg.CONF.keystone_authtoken.auth_uri
        creds['cacert'] = cfg.CONF.keystone_authtoken.cafile
        creds['endpoint_type'] = 'internalURL'
        nova = NovaHealth(creds)
        return nova.nova_hypervisor_list()

    def load(self):
        self.os_node_info_obj = openstack_node_info_reader(
            cfg.CONF.operator_test.operator_setup_file)

    @base.scenario(admin_only=False, operator=True)
    def rabbitmq_check(self):
        self.load()
        anscmd = "ansible -o all  -i 127.0.0.1, -a "
        cmd = "rabbitmqctl cluster_status -q"

        is_containerized = cfg.CONF.operator_test.containerized
        if is_containerized:
            rabbit_container = get_container_name('rabbitmq')
            cmd = ("'docker exec %s %s'" % (rabbit_container, cmd))

        cmd = anscmd + cmd + " -u root "

        res = execute(cmd)

        if not res['status']:
            node_status = res['output']
            node_status_string = node_status.replace('\\n', '')
            node_status_string = node_status_string.replace(' ', '')

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
                return (404, ("Failed Nodes : %s" %
                              str(diffnodes)))
            else:
                return (200, "Running Nodes : %s" % str(nodes),
                        ['RabbitMQ-server Running'])
        else:
            return (404, ("RabbitMQ-server test failed :%s" %
                          "rabbitmq-service is down", []))

    @base.scenario(admin_only=False, operator=True)
    def galera_check(self):
        self.load()
        anscmd = "ansible -o all  -i 127.0.0.1, -a "
        galera = self.os_node_info_obj.get_galera_details()

        cmd = ((r'mysql -u %s -p%s -e "SHOW STATUS;"') %
               (galera['username'], galera['password']))

        is_containerized = cfg.CONF.operator_test.containerized
        if is_containerized:
            galera_container = get_container_name('mariadb')

        cmd = ("'docker exec %s %s'" % (galera_container, cmd))
        cmd = anscmd + cmd + ' -u root'

        res = execute(cmd)

        if not res['status']:
            galera_status = res['output']
            if 'wsrep_incoming_addresses' not in galera_status:
                return (404, ("Galera Cluster Test Failed: %s" %
                              "Invalid cluster status", []))
            galera_status_string = galera_status.replace('\\n', '')
            mathobj = re.search(r'wsrep_incoming_addresses\s+(.*?)wsrep.*$',
                                galera_status_string, re.M | re.I)
            nodes = mathobj.group(1)
            return (200, "Active Nodes : %s" % nodes,
                    ['Galera Cluster Test Passed'])
        else:
            return (404, ("Galera Cluster Test Failed: %s" %
                          "service access failed", []))

    @base.scenario(admin_only=False, operator=True)
    def docker_check(self):
        self.load()
        node_list = self.os_node_info_obj.get_host_list()

        nodeip_list = [node.ip for node in node_list]
        anscmd = "ansible -o  all  -i %s -a " % ','.join(nodeip_list)
        cmd = "'docker ps -aq --filter %s '" % "status=exited"
        cmd = anscmd + cmd + ' -u root'

        res = execute(cmd)
        docker_failed = None

        if not res['status']:
            res['output'] = res['output'].split('\n')
            output = filter(lambda x: not re.match(r'^\s*$', x), res['output'])

            for line in output:
                line = line.split('|')
                if len(line) < 3:
                    continue
                if 'SUCCESS' not in line[1]:
                    if docker_failed:
                        docker_failed = docker_failed + ',' + line[0]
                    else:
                        docker_failed = line[0]
                else:
                    line[3] = line[3].replace(' ', '')
                    line[3] = line[3].replace('(stdout)', '')
                    if not re.match(r'^\s*$', line[3]):
                        if docker_failed:
                            docker_failed = docker_failed + ',' + line[0]
                        else:
                            docker_failed = line[0]
            if docker_failed:
                return (404, docker_failed, [])
            else:
                return (200, "All docker containers are up",
                        ['Docker container Test Passed'])
        else:
            return (404, ("Docker Check Failed: %s" %
                          "docker daemon not accessible", []))

    @base.scenario(admin_only=False, operator=True)
    def ceph_check(self):
        self.load()

        storage_nodes_from_ansible_config = [node.name.lower()
                                             for node in
                                             self.os_node_info_obj
                                             .get_host_list()
                                             if node.role == "block_storage"]

        if storage_nodes_from_ansible_config:
            cmd = (r"ceph -f json status")
            is_containerized = cfg.CONF.operator_test.containerized
            if is_containerized:
                ceph_container = get_container_name("ceph")
                cmd = ("'docker exec %s %s'" % (ceph_container, cmd))
            anscmd = "ansible -o all  -i 127.0.0.1, -a "
            cmd = anscmd + cmd + ' -u root'

            res = execute(cmd)
            if not res['status']:
                ceph_status = res['output']

                ceph_status = ceph_status.replace('\n', '')
                ceph_data = ceph_status.split('|')
                ceph_str = ceph_data[3].replace(' (stdout) ', '') \
                    .replace('\\n', '')
                ceph_json = simplejson.loads(ceph_str)
                overall_status = ceph_json['health']['overall_status']
                num_of_osd = ceph_json['osdmap']['osdmap']['num_osds']
                num_up_osds = ceph_json['osdmap']['osdmap']['num_up_osds']
                if overall_status == 'HEALTH_OK':
                    return (200, "Overall Status = %s, "
                                 "Cluster status = %s/%s" %
                            (overall_status, num_up_osds, num_of_osd))
                else:
                    return (404, "Overall Status = %s, "
                                 "Cluster status = %s/%s" %
                            (overall_status, num_up_osds, num_of_osd))
            else:
                return (300, ("Ceph cluster test skipped "
                              "as no dedicated storage found"))

    @base.scenario(admin_only=False, operator=True)
    def node_check(self):
        failed_hosts = None
        self.load()
        nodes_from_ansible_config = [node.name.lower()
                                     for node in
                                     self.os_node_info_obj.get_host_list()
                                     if node.role == "compute"]
        nova_hypervisor_list = self._get_nova_hypervior_list()
        if nova_hypervisor_list[0] != 200:
            return (404, ("Cannot get hypervisor list from "
                          "Nova reason-%sa") % nova_hypervisor_list[1])
        nodes_from_nova = [node.lower() for node in nova_hypervisor_list[2]]
        extra_nodes_nova = set(
            nodes_from_nova) - set(nodes_from_ansible_config)
        extra_nodes_ansible = set(
            nodes_from_ansible_config) - set(nodes_from_nova)
        if extra_nodes_nova:
            return (404, ("Hypervisors in nova hypervisor list are more"
                          " than configured.nova hypervisor list = %s") %
                    nodes_from_nova)
        if extra_nodes_ansible:
            return (404, ("Hypervisors in nova hypervisor list are less"
                          " than configured.nova hypervisor list = %s") %
                    nodes_from_nova)

        anscmd = ("ansible -o all  -i '%s' -m ping -u root" %
                  ','.join(nova_hypervisor_list[2]))
        res = execute(anscmd)
        res['output'] = res['output'].split('\n')
        output = filter(lambda x: not re.match(r'^\s*$', x), res['output'])
        for line in output:
            if "SUCCESS" not in line:
                failed_hosts = failed_hosts + line.split('|')[0]

        if not res['status']:
            return (200, "All nodes are up.nova hypervisor list = %s" %
                    nodes_from_nova)
        else:
            msg = "Some nodes are not up"
            if failed_hosts:
                msg = ("The following nodes are not up: %s."
                       "nova hypervisor list = %s" %
                       (str(failed_hosts[0]), nodes_from_nova))
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
