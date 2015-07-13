import ansible.runner
import ansible.inventory
import sys
import os
from openstack_node_info_reader import openstack_node_info_reader
from openstack_node import openstack_node_obj

TMP_LOCATION = "/tmp/sec_hc/"

class ansible_runner(object):
    def __init__(self,
                 os_node_list=[]):
        self.openstack_node = os_node_list
        #print self.openstack_node
        self.remote_user=None
        self.remote_pass=None
        self.inventory=None


    def execute_cmd(self,command,file_list=[],ips=[],roles=[]):
        inventory = None
        filetered_os_list = []
        if ips:
            filetered_os_list = self.get_os_node_list(ip_list=ips)
        elif roles:
            filetered_os_list = self.get_os_node_list(role_list=roles)
        else:
            filetered_os_list = self.openstack_node
        print filetered_os_list
        if filetered_os_list:
            inventory = self.init_ansible_inventory(filetered_os_list)
        if inventory:
            self.inventory = inventory
            for f in file_list:
                self.copy(f,TMP_LOCATION)
            out = self.execute(command+" >> "+TMP_LOCATION+"output")
            print out
            out = self.fetch(TMP_LOCATION+"output",TMP_LOCATION+"output",'no')
            print out
            out = self.execute("rm -rf /tmp/sec_hc/")
            print out

    def set_ansible_inventory(self,inv):
        self.inventory = inv

    def set_credential(self,user,passwd):
        self.remote_user = user
        self.remote_pass = passwd

    def init_ansible_inventory(self,os_node_list):
        ip_list=[]
        for os_node in self.openstack_node:
            ip_list.append(os_node.getIp())
            self.remote_user = os_node.getUser()
            self.remote_pass = os_node.getPassword()
        #print ip_list
        inventory = ansible.inventory.Inventory(ip_list)
        return inventory

    def get_os_node_list(self,ip_list=[],role_list=[]):
        filetered_list = []
        if not ip_list and not role:
            return self.openstack_node
        if ip_list and self.openstack_node:
            for ip in ip_list:
                for os_node in self.openstack_node:
                    if ip == os_node.getIp():
                        filetered_list.append(os_node)
        elif role_list and self.openstack_node:
            for role in role_list:
                for os_node in self.self.openstack_node:
                    if role == os_node.getRole():
                        filetered_list.append(os_node)
        return filetered_list


    def copy(self,src,dest):
        runner = ansible.runner.Runner(
            module_name='copy',
            module_args='src=%s dest=%s'%(src,dest),
            remote_user=self.remote_user,
            remote_pass=self.remote_pass,
            inventory = self.inventory,
        )
        out = runner.run()
        return out

    def fetch(self,src,dest,flat='yes'):
        runner = ansible.runner.Runner(
            module_name='fetch',
            module_args='src=%s dest=%s flat=%s'%(src,dest,flat),
            remote_user=self.remote_user,
            remote_pass=self.remote_pass,
            inventory = self.inventory,
        )
        out = runner.run()
        return out

    # can perform all shell operations Ex: rm /tmp/output
    def execute(self,command):
        #print command
        runner = ansible.runner.Runner(
            module_name='shell',
            module_args=command,
            remote_user=self.remote_user, 
            remote_pass=self.remote_pass,
            inventory = self.inventory,
        )
        out = runner.run()
        return out        

    def get_results(self):
        files = os.walk(TMP_LOCATION+'output/').next()[1]
        result ={}
        for f in files:
            try:
                result[f] = open(TMP_LOCATION+'output/'+f+TMP_LOCATION+'output','r').read()
            except IOError as e:
                print "Error opening the file : "+TMP_LOCATION+'output/'+f+TMP_LOCATION+'output'
        return result


if __name__ == '__main__':
    os_node_info_obj = openstack_node_info_reader("/home/ubuntu/sasi/cpulse/cloudpulse/plugins/security_pulse/config/openstack_config.yaml")
    openstack_node_list = os_node_info_obj.get_host_list()
    print openstack_node_list
    flist=["/home/ubuntu/sasi/cpulse/cloudpulse/plugins/security_pulse/testcase/TLS_Enablement_Check.py"]
    ans_runner = ansible_runner(openstack_node_list)
    ans_runner.execute_cmd("python "+TMP_LOCATION+"TLS_Enablement_Check.py",file_list=flist)
