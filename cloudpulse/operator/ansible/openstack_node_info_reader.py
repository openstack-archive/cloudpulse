import yaml
import os
from openstack_node import openstack_node_obj

class openstack_node_info_reader(object):

    def __init__(self,os_node_file):
        
        self.hostYamlObj = None

        try:
            fp = open(os_node_file)
        except IOError as e:
            print "Error while opening the file...%s" % e
            return
        try:
            self.hostYamlObj = yaml.load(fp)
        except yaml.error.YAMLError as perr:
            print "Error while parsing...%s" % perr
            return

    def get_host_list(self):
        openstack_host_list = []
        for key in self.hostYamlObj.keys():
            name = key
            ip = self.hostYamlObj[key]["ip"]
            hostname = key
            username = self.hostYamlObj[key]["user"]
            password = self.hostYamlObj[key]["password"]
            role = self.hostYamlObj[key]["role"]
            node_obj = openstack_node_obj(hostname,ip,username,password,role,name)
            openstack_host_list.append(node_obj)
        return openstack_host_list

    """
    def get_host_list(self):
        return self.openstack_host_list
    """

    def printHostList(self,openstack_host_list):
        for hostObj in openstack_host_list:
            print "%s - %s - %s" % (hostObj.getIp(),hostObj.getHost(),
                                         hostObj.getUser())

if __name__ == '__main__':
    os_node_info_obj = openstack_node_info_reader()
    os_node_info_obj.get_host_list()
    

