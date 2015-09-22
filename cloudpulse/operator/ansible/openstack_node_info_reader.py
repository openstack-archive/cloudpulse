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
from openstack_node import openstack_node_obj
import yaml


class openstack_node_info_reader(object):

    def __init__(self, os_node_file):
        self.hostYamlObj = None
        try:
            fp = open(os_node_file)
        except IOError as e:
            print ("Error while opening the file...%s", e)
            return
        try:
            self.hostYamlObj = yaml.load(fp)
        except yaml.error.YAMLError as perr:
            print ("Error while parsing...%s", perr)
            return

    def get_host_list(self):
        openstack_host_list = []
        for key in self.hostYamlObj.keys():
            name = key
            ip = self.hostYamlObj[key]["ip"]
            hostname = key
            username = self.hostYamlObj[key]["user"]
            role = self.hostYamlObj[key]["role"]
            node_obj = openstack_node_obj(hostname, ip, username,
                                          role, name)
            openstack_host_list.append(node_obj)
        return openstack_host_list

    """
    def get_host_list(self):
        return self.openstack_host_list
    """

    def printHostList(self, openstack_host_list):
        for hostObj in openstack_host_list:
            print ("%s - %s - %s", hostObj.getIp(),
                   hostObj.getHost(), hostObj.getUser())

    def get_galera_details(self):
        galera = {}
        print(self.hostYamlObj)
        for key in self.hostYamlObj.keys():
            if 'galerauser' in self.hostYamlObj[key].keys():

                galera['username'] = self.hostYamlObj[key]['galerauser']
                galera['password'] = self.hostYamlObj[key]['galerapassword']
        return galera

"""
if __name__ == '__main__':
    os_node_info_obj = openstack_node_info_reader()
    os_node_info_obj.get_host_list()
"""
