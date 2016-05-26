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
import ansible.constants as CONST
import ansible.inventory
import ansible.runner
import cloudpulse
from cloudpulse.scenario.plugins.security_pulse.util.\
    security_pulse_test_input import security_test_input_reader
import json
import os


def get_temp_path():
    base_dir = os.path.dirname(cloudpulse.__file__)
    try:
        config_file = base_dir + '/scenario/plugins/security_pulse/config/' +\
            'securityhealth_test_input.yaml'
        input_reader = security_test_input_reader(config_file)
        input_data = input_reader.process_security_input_file()
        return input_data['global_data']['file_info_dir']
    except Exception:
        print ("Exception while getting temp path..")
        return "/var/sec_hc/"

CONST.HOST_KEY_CHECKING = False
TMP_LOCATION = get_temp_path()

is_containerized = False


class ansible_runner(object):

    def __init__(self, os_node_list=[]):
        self.openstack_node = os_node_list
        self.remote_user = None
        self.inventory = None

    def execute_cmd(self, command, file_list=[], ips=[], roles=[],
                    container_name=None):
        inventory = None
        filetered_os_list = []
        if ips:
            filetered_os_list = self.get_os_node_list(ip_list=ips)
        elif roles:
            filetered_os_list = self.get_os_node_list(role_list=roles)
        else:
            filetered_os_list = self.openstack_node
        # print filetered_os_list
        if filetered_os_list:
            inventory = self.init_ansible_inventory(filetered_os_list)
        if inventory:
            self.inventory = inventory
            if is_containerized:
                self.execute("mkdir " + TMP_LOCATION,
                             container_name=container_name)
            for f in file_list:
                self.copy(f, TMP_LOCATION, container_name=container_name)
            out = self.execute(command, container_name=container_name)
            print (out)
            # remove the files from containers
            self.execute("rm -rf " + TMP_LOCATION,
                         container_name=container_name)
            if is_containerized:
                # remove the files from host
                self.execute("rm -rf " + TMP_LOCATION)
            return out

    def set_ansible_inventory(self, inv):
        self.inventory = inv

    def set_credential(self, user):
        self.remote_user = user

    def init_ansible_inventory(self, os_node_list):
        ip_list = []
        for os_node in os_node_list:
            ip_list.append(os_node.getIp())
            self.remote_user = os_node.getUser()
        inventory = ansible.inventory.Inventory(ip_list)
        return inventory

    def get_os_node_list(self, ip_list=[], role_list=[]):
        filetered_list = []
        if not ip_list and not role_list:
            return self.openstack_node
        if ip_list and self.openstack_node:
            for ip in ip_list:
                for os_node in self.openstack_node:
                    if ip == os_node.getIp():
                        filetered_list.append(os_node)
        elif role_list and self.openstack_node:
            for role in role_list:
                for os_node in self.openstack_node:
                    if role == os_node.getRole():
                        filetered_list.append(os_node)
        return filetered_list

    def copy(self, src, dest, container_name=None):
        runner = ansible.runner.Runner(
            module_name='copy',
            module_args='src=%s dest=%s' % (src, dest),
            remote_user=self.remote_user,
            inventory=self.inventory,
            forks=1,
        )
        out = runner.run()
        print (out)
        # copy to container
        if is_containerized:
            con_runner = self.container_copy(src, dest, container_name)
            out1 = con_runner.run()
            print (out1)
        return out

    def container_copy(self, src, dest, container_name):
        new_src = TMP_LOCATION + src.split('/')[-1]
        dest = dest + src.split('/')[-1]
        cmd = "docker exec -i %s sh -c 'cat > %s' < %s" \
            % (container_name, dest, new_src)
        runner = ansible.runner.Runner(
            module_name='shell',
            module_args=cmd,
            remote_user=self.remote_user,
            # remote_pass=self.remote_pass,
            inventory=self.inventory,
            forks=1,
        )
        print (cmd)
        return runner

    def fetch(self, src, dest, flat='yes'):
        runner = ansible.runner.Runner(
            module_name='fetch',
            module_args='src=%s dest=%s flat=%s' % (src, dest, flat),
            remote_user=self.remote_user,
            inventory=self.inventory,
            forks=1,
        )
        out = runner.run()
        return out

    # can perform all shell operations Ex: rm /tmp/output
    def execute(self, command, container_name=None, roles=[]):
        filetered_os_list = []
        if roles:
            filetered_os_list = self.get_os_node_list(role_list=roles)
            self.inventory = self.init_ansible_inventory(filetered_os_list)
        if is_containerized and container_name:
            command = 'docker exec %s %s' % (container_name, command)

        # print command
        runner = ansible.runner.Runner(
            module_name='shell',
            module_args=command,
            remote_user=self.remote_user,
            inventory=self.inventory,
            forks=1,
        )
        out = runner.run()
        return out

    def ping(self, container_name=None, roles=[]):
        filetered_os_list = []
        if roles:
            filetered_os_list = self.get_os_node_list(role_list=roles)
            self.inventory = self.init_ansible_inventory(filetered_os_list)
        runner = ansible.runner.Runner(
            module_name='ping',
            remote_user=self.remote_user,
            inventory=self.inventory,
            timeout=30,
            forks=1,
        )
        out = runner.run()
        return out

    def get_results(self):
        result = {}
        if not os.path.isdir(TMP_LOCATION + 'output/'):
            return result
        files = os.walk(TMP_LOCATION + 'output/').next()[1]
        for f in files:
            try:
                result[f] = open(TMP_LOCATION + 'output/' +
                                 f + TMP_LOCATION + 'output', 'r').read()
            except IOError:
                print ("Error opening the file : " + TMP_LOCATION +
                       'output/' + f + TMP_LOCATION + 'output')
        return result

    def validate_results(self, results, checks=None):
        results['status'] = 'PASS'
        failed_hosts = []

        if results['dark']:
            failed_hosts.append(results['dark'].keys())
            results['status'] = 'FAIL'
            results['status_message'] = ''

        for node in results['contacted'].keys():
            if 'failed' in results['contacted'][node]:
                if results['contacted'][node]['failed'] is True:
                    results['status'] = 'FAIL'
                    results['status_message'] = " ".join(
                        [("%s -> %s") % (key, results['dark'][key])
                         for key in results['dark']])

        for node in results['contacted'].keys():
            rc = results['contacted'][node].get('rc', None)
            if rc is not None and rc != 0:
                failed_hosts.append(node)
                results['status'] = 'FAIL'
                results['status_message'] = results[
                    'contacted'][node].get('stderr', None)

        if checks is None:
            # print "No additional checks validated"
            return results, failed_hosts

        for check in checks:
            key = check.keys()[0]
            value = check.values()[0]
            for node in results['contacted'].keys():
                if key in results['contacted'][node].keys():
                    if results['contacted'][node][key] != value:
                        failed_hosts.append(node)
                        results['status'] = 'FAIL'
                        results['status_message'] = ''

        return (results, failed_hosts)

    def get_parsed_ansible_output(self, output_data):
        if output_data:
            return self.get_validated_data(output_data)
        else:
            msg = {
                'message': 'No result from test execution',
                'status': 'Fail'}
            return (404, json.dumps([msg], []))

    def get_validated_data(self, results):
        print ("Inside get_validated_data", results)
        # final_result = {}
        output = []
        status = 200  # 'PASS'
        ###################################################
        # First validation is to make sure connectivity to
        # all the hosts was ok.
        ###################################################
        if results['dark']:
            status = 404  # 'FAIL'

        ##################################################
        # Now look for status 'failed'
        ##################################################
        for node in results['contacted'].keys():
            if 'failed' in results['contacted'][node]:
                if results['contacted'][node]['failed'] is True:
                    status = 404  # 'FAIL'
                    msg = {
                        'node': node,
                        'status': 'Fail',
                        'message': 'Execution failed'}
                    output.append(msg)

        #################################################
        # Check for the return code 'rc' for each host.
        #################################################
        for node in results['contacted'].keys():
            rc = results['contacted'][node].get('rc', None)
            if rc is not None and rc != 0:
                status = 404  # 'FAIL'
            node_info = results['contacted'][node]
            op = eval(node_info.get('stdout'))
            if not op.get('OverallStatus'):
                status = 404  # 'FAIL'
            try:
                res = op.get('result', [])
                for tc in res:
                    tc.update({'node': node})
                    output.append(tc)
            except Exception:
                print ("Exception while getting the result" +
                       " from the ansible output")
        return (status, json.dumps(output), [])

"""
if __name__ == '__main__':
    os_node_info_obj = openstack_node_info_reader("/home/ubuntu/
        sasi/cpulse/cloudpulse/plugins/security_pulse/config/
        openstack_config.yaml")
    openstack_node_list = os_node_info_obj.get_host_list()
    print openstack_node_list
    flist=["/home/ubuntu/sasi/cpulse/cloudpulse/plugins/
    security_pulse/testcase/TLS_Enablement_Check.py"]
    ans_runner = ansible_runner(openstack_node_list)
    ans_runner.execute_cmd("python "+TMP_LOCATION+
        "TLS_Enablement_Check.py",file_list=flist)
"""
