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
from cloudpulse.scenario.plugins.operator_tests import utils
import os
import sys


class ConfigHelper(object):

    def __init__(self, host_file=None):
        if host_file is None:
            print("Host file not passed. exit")
            sys.exit(0)

        self.host_file = utils.get_absolute_path_for_file(__file__,
                                                          host_file)
        if not os.path.exists(self.host_file):
            print("%s file does not exist" % self.host_file)
            return

        self.parsed_data = utils.create_parsed_yaml(self.host_file)

    def get_host_ip_list(self, role=None):
        host_ip_list = []
        host_roles = self.parsed_data.get('ROLES', {})
        if role is not None:
            return host_roles.get(role)
        # if no role specified return all hosts
        for ip in host_roles.values():
            if ip is not None:
                host_ip_list.extend(ip)
        return host_ip_list

    def get_external_vip_interface(self):
        return self.parsed_data['VIP_INTERFACE']

    def get_internal_vip_interface(self):
        return self.parsed_data['MGMT_VIP_INTERFACE']

    def get_server_username(self):
        return self.parsed_data['SERVER_COMMON']['server_username']

    def get_server_pass(self):
        return self.parsed_data['SERVER_COMMON']['server_pass']

    def get_percona_username(self):
        return self.parsed_data['PERCONA']['percona_username']

    def get_percona_pass(self):
        return self.parsed_data['PERCONA']['percona_pass']

    def get_haproxy_internal_ip(self):
        return self.parsed_data.get('internal_lb_vip_address', None)

    def get_haproxy_external_ip(self):
        return self.parsed_data.get('external_lb_vip_address', None)

    def get_domain_name_servers(self):
        return self.parsed_data['NETWORKING']['domain_name_servers']

    def get_host_list(self):
        host_list = []

        host_list = self.parsed_data.keys()

        return host_list

    def get_host_username(self, hostname):
        host = self.parsed_data.get(hostname, None)
        if host is None:
            print("host with name %s not found" % hostname)
            return None

        return host.get('user', None)

    def get_host_password(self, hostname):
        host = self.parsed_data.get(hostname, None)
        if host is None:
            print("host with name %s not found" % hostname)
            return None

        return host.get('password', None)
