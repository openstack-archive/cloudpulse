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

import os
import subprocess

os_log_cfg_file = {'ceilometer': 'openstack-ceilometer',
                   'cinder': 'openstack-cinder',
                   'httpd': 'openstack-dashboard',
                   'glance': 'openstack-glance',
                   'keystone': 'openstack-keystone',
                   'neutron': 'openstack-neutron',
                   'nova': 'openstack-nova',
                   'swift': 'openstack-swift',
                   'rabbitmq': 'rabbitmq-server',
                   'mariadb': 'mariadb',
                   'mongodb': 'mongodb',
                   'heat': 'openstack-heat'}

os_service_name = ['nova', 'cinder', 'httpd', 'glance', 'keystone',
                   'neutron', 'ceilometer', 'swift', 'rabbitmq',
                   'mariadb', 'mongodb', 'heat']

logrotaion_dir = "/etc/logrotate.d/"


class LogRotateCheck(object):

    def find_openstack_service(self):
        output = subprocess.check_output('systemctl | grep -i  -e "mongo" \
                                        -e "maria" -e "httpd" -e "rabbit" \
                                        -e "openstack" | tr -s " " \
                                        | cut -d" " -f1', shell=True)
        running_service = output.split('\n')
        running_service.append('keystone')
        service_list = []
        for service_name in os_service_name:
            r = [s for s in running_service if service_name in s]
            if r:
                service_list.append(service_name)
        return service_list

    def log_rotate_check(self):
        try:
            result = []
            final_result = {}
            tmp = {}
            overall_status = True
            service_list = self.find_openstack_service()
            for service_name in service_list:
                cfg_file = os_log_cfg_file[service_name]
                if os.path.exists(logrotaion_dir + cfg_file):
                    cfg_lines = open(logrotaion_dir + cfg_file, "r").read().\
                        splitlines()
                    case_name = 'Log Rotate Check for ' + cfg_file
                    for line in cfg_lines:
                        if "/var/log" in line and not line.startswith('#'):
                            tmp[cfg_file] = "Config Exists"
                    if cfg_file not in tmp:
                        overall_status = False
                        res = {'status': 'Fail'}
                        res.update(
                            {'test_case_name': case_name})
                        res.update({'message': 'No Log Rotation Config Found'})
                        result.append(res)
                    else:
                        res = {'status': 'Pass'}
                        res.update(
                            {'test_case_name': case_name})
                        res.update({'message': 'Log Rotation Config Found'})
                        result.append(res)
                else:
                    # tmp[cfg_file] = "Log file doesn't exists"
                    overall_status = False
                    res = {'status': 'Fail'}
                    res.update(
                        {'test_case_name': case_name})
                    res.update({'message': "Log file doesnot exists"})
                    result.append(res)
            final_result.update(
                {'OverallStatus': overall_status})
            final_result.update({'result': result})
            print(final_result)
            return
        except Exception:
            final_result.update(
                {'OverallStatus': False})
            result = {}
            result.update({'test_case_name': 'Log Rotate Check'})
            result.update({'status': 'Fail'})
            result.update(
                {'message': 'Exception in log rotate check'})
            final_result.update({'result': [result]})
            print(final_result)
            return

if __name__ == '__main__':
    lrc = LogRotateCheck()
    lrc.log_rotate_check()
