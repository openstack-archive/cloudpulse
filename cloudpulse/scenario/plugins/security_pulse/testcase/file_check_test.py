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
import json
import os
import subprocess


class SecurityFileCheck(object):

    def perform_file_permission_check(self, input_params):
        try:
            print ("Executing the test ", input_params.get('testcase_name'))
            final_result = []
            final_status = []
            final_msg = []
            file_info_dir = input_params['global_data']['file_info_dir']
            is_containerized = input_params['global_data']['is_containerized']
            perform_on = input_params['perform_on']
            if perform_on is None or not perform_on:
                print ("Perform on should be mentioned either at test level" +
                       " or test case level")
                msg = {'message': 'Perform on should be mentioned either at' +
                       ' test level or test case level'}
                return (404, json.dumps([msg]), [])
            os_hostobj_list = input_params['os_host_list']
            base_dir = os.path.dirname(cloudpulse.__file__)
            baseline_file = input_params['baseline_file']
            flist = [base_dir +
                     "/scenario/plugins/security_pulse/testcase/" +
                     "remote_file_check.py",
                     base_dir + "/scenario/plugins/security_pulse/testcase/" +
                     "remote_filecredentials.py",
                     file_info_dir + "dir_list",
                     file_info_dir + "os_baseline"]

            def ConsolidateResults(flist, container_name=None):
                result = ans_runner.execute_cmd(
                    "python " +
                    file_info_dir +
                    "remote_file_check.py ",
                    file_list=flist, container_name=container_name)
                Result = ans_runner.get_parsed_ansible_output(result)
                final_status.append(Result[0])
                final_result.extend(ast.literal_eval(Result[1]))
                final_msg.extend(Result[2])

            for p in perform_on:
                for obj in os_hostobj_list:
                    ans_runner = ansible_runner([obj])
                    if obj.getRole() == p:
                        os_dir = input_params[p + '_dir']
                        all_baseline = ast.literal_eval(
                            open(baseline_file).read())
                        baseline = all_baseline[p]
                        open(
                            file_info_dir +
                            'os_baseline',
                            'w').write(
                            str(baseline))

                        # if container, make dir list and copy to container
                        if is_containerized:
                            for container, os_dir in os_dir.items():
                                self.createDirList(
                                    os_dir,
                                    file_info_dir)
                                ConsolidateResults(
                                    flist,
                                    container_name=container)
                                subprocess.call([
                                    'rm',
                                    file_info_dir +
                                    'dir_list'])

                        else:
                            os_dir_list = []
                            [os_dir_list.extend(d) for d in os_dir.values()]
                            # os_dir = os_dir.values()
                            self.createDirList(os_dir_list, file_info_dir)
                            # flist.append("/tmp/sec_hc/dir_list")
                            ConsolidateResults(flist)
            subprocess.call([
                'rm', '-rf',
                file_info_dir +
                'os_baseline',
                file_info_dir +
                'output'])
            subprocess.call([
                'rm',
                file_info_dir +
                'dir_list'])
            if 404 in final_status:
                return (404, final_result, final_msg)
            else:
                return (200, final_result, final_msg)
        except Exception as e:
            print ("exception in perform_file_permission_check is--", e)
            subprocess.call([
                'rm', '-rf',
                file_info_dir +
                'os_baseline',
                file_info_dir +
                'output'])
            subprocess.call([
                'rm',
                file_info_dir +
                'dir_list'])
            print (
                "Exception occured in executing" +
                " perform_file_permission_check")
            message = {
                'message': 'Test case execution failed due to some exception'}
            return (404, json.dumps([message]), [])

    def createDirList(self, os_dir, file_info_dir):
        if os_dir is not None:
            f = open(file_info_dir + 'dir_list', 'w+')
            for dir_name in os_dir:
                f.write(dir_name + '\n')
            f.close()

if __name__ == '__main__':
    sec = SecurityFileCheck()
    sec.perform_file_permission_check()
