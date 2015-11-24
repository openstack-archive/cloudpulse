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
import os
import pwd
import remote_filecredentials as filecredentials
import stat
import string


class FileCheck(object):

    def file_check(self, dir_list, file_dir):
        try:
            output = {}
            result = []
            final_result = {}
            overall_status = True
            for dir_name in dir_list:
                self.rootDir = dir_name
                for dirName, subdirList, fileList in os.walk(self.rootDir):
                    # flist = []
                    # for f in fileList:
                    #    flist.append(os.path.abspath(os.path.join(dirName,f)))
                    os.chdir(dirName)
                    for f1 in fileList:  # flist
                        st = os.stat(f1)
                        ins = filecredentials.AccessPreveliges(
                            f1, st[stat.ST_SIZE], oct(
                                stat.S_IMODE(
                                    st[
                                        stat.ST_MODE])), pwd.getpwuid(
                                st[stat.ST_UID]), pwd.getpwuid(
                                st[stat.ST_GID]))
                        output.update(
                            {
                                ins.getName(): {
                                    'size': ins.getSize(),
                                    'mode': ins.getMode(),
                                    'user': ins.getUser(),
                                    'group': ins.getGroup()}})
            keystone_baseline = ast.literal_eval(
                open(file_dir + 'os_baseline').read())
            remote_mismatch = list(set(output.keys()).
                                   difference(keystone_baseline.keys()))
            baseline_mismatch = list(set(keystone_baseline.keys()).
                                     difference(output.keys()))
            for key in output.keys():
                if key in keystone_baseline:
                    new = output.get(key)
                    base = keystone_baseline[key]
                    diffkeys = [k for k in base if base[k] != new[k]]
                    l = []
                    for k in diffkeys:
                        l.append(
                            '"' +
                            k +
                            '"' +
                            ' is modified from ' +
                            base[k] +
                            ' to ' +
                            new[k] +
                            ' in remote')
                    msg = string.join(l, ', ')
                    if msg:
                        temp = {'test_case_name': key, 'Status': 'Fail'}
                        temp.update({'message': msg})
                        result.append(temp)
            if baseline_mismatch:
                for item in baseline_mismatch:
                    msg = 'File not found in remote'
                    temp = {'test_case_name': item, 'Status': 'Fail'}
                    temp.update({'message': msg})
                    result.append(temp)
            if remote_mismatch:
                for item in remote_mismatch:
                    msg = 'New file found in remote'
                    temp = {'test_case_name': item, 'Status': 'Fail'}
                    temp.update({'message': msg})
                    result.append(temp)
            if not result:
                overall_status = True
                final_result.update(
                    {'OverallStatus': overall_status})
                result = {}
                result.update({'test_case_name': 'File permission Check'})
                result.update({'status': 'Pass'})
                result.update({'message': 'No mismatch'})
                final_result.update({'result': [result]})
                print (final_result)
                return
            else:
                final_result.update(
                    {'OverallStatus': False})
                final_result.update({'result': result})
                print (final_result)
                return
        except Exception as e:
            final_result.update(
                {'OverallStatus': False})
            result = {}
            result.update({'test_case_name': 'File permission Check'})
            result.update({'status': 'Fail'})
            result.update(
                {'message': 'Exception in file comparision' + str(e)})
            final_result.update({'result': [result]})
            print (final_result)
            return

if __name__ == '__main__':
    file_dir = '/var/sec_hc/'
    dirs = []
    with open(file_dir + 'dir_list') as f:
        dirs = f.read().splitlines()
    sec = FileCheck()
    sec.file_check(dirs, file_dir)
