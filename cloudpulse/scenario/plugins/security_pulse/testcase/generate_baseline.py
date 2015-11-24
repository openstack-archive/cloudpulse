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

import ast
import cloudpulse
from cloudpulse.operator.ansible.ansible_runner import ansible_runner
from cloudpulse.operator.ansible import openstack_config_reader as os_cfg
import json
import os
import sys


class BaseLine(object):

    def base_line(self, os_baseline_cfg):
        try:
            oscfg_reader = os_cfg.os_cfg_reader(os_baseline_cfg)
            oscfg_reader.setOpenstackNodeIp()
            oscfg_reader.printHostList()
            openstack_host_list = oscfg_reader.get_host_list()
            baseline_data = {}
            for host in openstack_host_list:
                f = open('/var/sec_hc/dir_list', 'w+')
                for dir_name in host.getDirList():
                    f.write(dir_name + '\n')
                f.close()
                ans_runner = ansible_runner([host])
                # execute_cmd
                base_dir = os.path.dirname(cloudpulse.__file__)
                base_dir += '/scenario/plugins/security_pulse/testcase'
                flist = [base_dir + '/remote_baseline.py',
                         base_dir + '/remote_filecredentials.py',
                         '/var/sec_hc/dir_list'
                         ]
                results = ans_runner.execute_cmd(
                    "python " +
                    '/var/sec_hc/' +
                    "remote_baseline.py ",
                    file_list=flist)
                # for node in results['contacted'].keys():
                role = host.getRole()
                node = host.getIp()
                data = results['contacted'][node]['stdout']

                baseline_data.update({role: ast.literal_eval(data)})
                print (baseline_data)
            formated_data = json.dumps(baseline_data, indent=4)
            open('/var/sec_hc/os_allnode_baseline',
                 'w+').write(str(formated_data))
        except Exception as e:
            print (e)

if __name__ == '__main__':
    os_cfg_file = sys.argv[1]
    sec = BaseLine()
    sec.base_line(os_cfg_file)
