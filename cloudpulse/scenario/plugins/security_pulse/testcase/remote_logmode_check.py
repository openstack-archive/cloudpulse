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

import ConfigParser
import os


class LogModeCheck(object):

    def log_mode_check(self, dir_list):
        try:
            result = []
            final_result = {}
            overall_status = True
            if dir_list is None or not dir_list:
                res = {'message': 'Directory list is empty',
                       'status': 'Fail', 'test_case_name': 'Log Mode Check'}
                result.append(res)
                final_result.update(
                    {'OverallStatus': False})
                final_result.update({'result': result})
                print(final_result)
                return
            config = ConfigParser.ConfigParser()
            for dir_name in dir_list:
                for dirName, subdirList, files in os.walk(dir_name):
                    files = [file for file in files if file.
                             endswith(('.conf', '.ini'))]
                    for f1 in files:
                        debug_msg = {}
                        verbose_msg = {}
                        abspath = ''
                        if dirName.endswith("/"):
                            abspath = dirName + f1
                        else:
                            abspath = dirName + "/" + f1
                        case_name = "Debug Mode check for '" + abspath + "'"
                        debug_msg.update(
                            {'test_case_name': case_name})
                        verbose_msg.update({'test_case_name': "Verbose Mode" +
                                            " check for '" + abspath + "'"})
                        try:
                            config.read(abspath)
                        except Exception:
                            continue
                        try:
                            config.get("DEFAULT", "debug")
                        except ConfigParser.NoOptionError as e:
                            msg = 'Debug option is not enabled'
                            debug_msg.update(
                                {'message': msg})
                            debug_msg.update({'status': 'Pass'})
                        else:
                            debug = config.get("DEFAULT", "debug")
                            if debug.lower() == 'false':
                                msg = "Debug option is enabled with 'false'"
                                debug_msg.update(
                                    {'message': msg})
                                debug_msg.update({'status': 'Pass'})
                            else:
                                msg = 'Debug option is enabled'
                                debug_msg.update(
                                    {'message': msg})
                                debug_msg.update({'status': 'Fail'})
                                overall_status = False
                        result.append(debug_msg)

                        try:
                            config.get("DEFAULT", "verbose")
                        except ConfigParser.NoOptionError:
                            msg = 'Verbose option is not enabled'
                            verbose_msg.update(
                                {'message': msg})
                            verbose_msg.update({'status': 'Pass'})
                        else:
                            verbose = config.get("DEFAULT", "verbose")
                            if verbose.lower() == 'false':
                                msg = "Verbose option is enabled with 'false'"
                                verbose_msg.update(
                                    {'message': msg})
                                verbose_msg.update({'status': 'Pass'})
                            else:
                                msg = 'Verbose option is enabled'
                                verbose_msg.update(
                                    {'message': msg})
                                verbose_msg.update({'status': 'Fail'})
                                overall_status = False
                        result.append(verbose_msg)
            final_result.update(
                {'OverallStatus': overall_status})
            final_result.update({'result': result})
            print(final_result)
            return
        except Exception as e:
            final_result.update(
                {'OverallStatus': False})
            result = {}
            result.update({'test_case_name': 'Log Mode Check'})
            result.update({'status': 'Fail'})
            result.update(
                {'message': 'Exception in log mode check' + str(e)})
            final_result.update({'result': [result]})
            print(final_result)
            return

if __name__ == '__main__':
    file_dir = '/var/sec_hc/'
    dirs = []
    with open(file_dir + 'dir_list') as f:
        dirs = f.read().splitlines()
    sec = LogModeCheck()
    sec.log_mode_check(dirs)
