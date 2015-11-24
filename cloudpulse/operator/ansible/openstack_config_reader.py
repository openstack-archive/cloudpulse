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
from hostObj import HostObject
import os
import yaml


class os_cfg_reader(object):

    def __init__(self, hostFileName="openstack_config.yaml"):
        abs_path = os.getcwd() + os.sep + 'config/%s' % hostFileName
        self.hostYamlObj = None
        self.openstack_host_list = []
        try:
            fp = open(abs_path)
        except IOError as e:
            print ("Error while opening the file...%s" % e)
            return

        try:
            self.hostYamlObj = yaml.safe_load(fp)
            # print "self.hostYamlObj: ", self.hostYamlObj,
            # dir(self.hostYamlObj)
        except yaml.error.YAMLError as perr:
            print ("Error while parsing...%s" % perr)
            return

    def setOpenstackNodeIp(self):
        # print self.hostYamlObj
        for key in self.hostYamlObj.keys():
            name = key
            ip = self.hostYamlObj[key]["ip"]
            hostname = key
            username = self.hostYamlObj[key]["user"]
            role = self.hostYamlObj[key]["role"]
            hstObj = HostObject(
                hostname,
                ip,
                username,
                role,
                name,
                False)
            if "dirlist" in self.hostYamlObj[key]:
                dirList = self.hostYamlObj[key]["dirlist"]
                hstObj.setDirList(dirList)
            self.openstack_host_list.append(hstObj)

    def get_host_list(self):
        return self.openstack_host_list

    def printHostList(self):
        for hostObj in self.openstack_host_list:
            print ("IP - %s" % (hostObj.getIp()))
            print ("HOST - %s" % (hostObj.getHost()))
            print ("USER - %s" % (hostObj.getUser()))
            print ("NAGIOS RUNNING - %s" % (str(hostObj.isNagiosRunning())))

    def generate_ansible_config(self, os_obj_list):
        f = open('/var/sec_hc/ansible_hosts', 'w+')
        for obj in os_obj_list:
            # print obj.getName()
            f.write('[' + obj.getName() + ']\n')
            f.write(
                obj.getIp() +
                '\t\t' +
                'ansible_ssh_user=' +
                obj.getUser() +
                '\t\tansible_ssh_pass=' +
                obj.getPassword())
            f.write('\n')
        f.close()
"""

    def update_ansible_playbook(self):
        f = open('testcase-configs/ansible-playbook.yaml')
        f1 = open('testcase-configs/ansible-playbook_update.yaml', "w")
        for line in f:
            if 'hosts' in line:
                f1.write('- hosts: sasi1\n')
            else:
                f1.write(line)
        f.close()
        f1.close()
"""
if __name__ == '__main__':
    yhp = os_cfg_reader()
    yhp.setOpenstackNodeIp()
    yhp.printHostList()
    # yhp.generate_ansible_config(yhp.get_host_list())
    yhp.update_ansible_playbook()
