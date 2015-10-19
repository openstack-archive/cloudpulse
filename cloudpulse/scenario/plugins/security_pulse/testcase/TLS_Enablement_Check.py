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
import ConfigParser
import os
import pwd
import stat


class tls_enable_check(object):

    def __init__(self):
        pass

    def read_tls_config(self, config):
        Result = {}
        final_result = {}
        overall_status = True
        try:
            config.get("ldap", "use_tls")
        except ConfigParser.NoOptionError:
            overall_status = False
            final_result.update({'OverallStatus': overall_status})
            msg = {
                'Test Case Name': 'TLS',
                'Message': 'use_tls option is not enabled',
                'Status': 'Fail'}
            Result.update(msg)
            final_result.update({'result': [Result]})
            print (final_result)
            return
        else:
            use_tls = config.get("ldap", "use_tls")
            if use_tls == 'false':
                overall_status = False
                final_result.update({'OverallStatus': overall_status})
                msg = {
                    'Test Case Name': 'TLS',
                    'Message': "use_tls option is enabled with 'false' value",
                    'Status': 'Fail'}
                Result.update(msg)
                final_result.update({'result': [Result]})
                print (final_result)
                return
            elif use_tls == 'true':
                ca_dir = None
                try:
                    ca_dir = config.get("ldap", "tls_cacertdir")
                except ConfigParser.NoOptionError:
                    try:
                        tls_ca_file = config.get("ldap", "tls_cacertfile")
                        ca_dir = tls_ca_file[:tls_ca_file.rindex('/')]
                    except ConfigParser.NoOptionError:
                        overall_status = False
                        final_result.update({'OverallStatus': overall_status})
                        msg = {
                            'Test Case Name': 'TLS',
                            'Message': "Both 'tls_ca_dir' and" +
                            " 'tls_ca_file' are not defined",
                            'Status': 'Fail'}
                        Result.update(msg)
                        final_result.update({'result': [Result]})
                        print (final_result)
                        return
                if not ca_dir:
                    overall_status = False
                    final_result.update({'OverallStatus': overall_status})
                    msg = {
                        'Test Case Name': 'TLS',
                        'Message': "Both 'tls_ca_dir' and" +
                        " 'tls_ca_file' are not defined",
                        'Status': 'Fail'}
                    Result.update(msg)
                    final_result.update({'result': [Result]})
                    print (final_result)
                    return
                else:
                    for dirName, subdirList, fileList in os.walk(ca_dir):
                        os.chdir(dirName)
                        for f1 in fileList:
                            st = os.stat(f1)
                            user = pwd.getpwuid(st[stat.ST_UID])[0]
                            group = pwd.getpwuid(st[stat.ST_GID])[0]
                            if user != 'keystone' or group != 'keystone':
                                msg = "Certificate file directory " + \
                                    " user/group permission are user=" + user \
                                    + ", group=" + group
                                overall_status = False
                                final_result.update(
                                    {'OverallStatus': overall_status})
                                res = {
                                    'Test Case Name': 'TLS',
                                    'Message': msg,
                                    'Status': 'Fail'}
                                Result.update(res)
                                final_result.update({'result': [Result]})
                                print (final_result)
                                return
                final_result.update({'OverallStatus': overall_status})
                msg = {
                    'Test Case Name': 'TLS',
                    'Message': "TLS is enabled and the Certificate file" +
                    " permissions are 'keystone'",
                    'Status': 'Pass'}
                Result.update(msg)
                final_result.update({'result': [Result]})
                print (final_result)
                return

if __name__ == '__main__':
    tls_enable_check_obj = tls_enable_check()
    config = ConfigParser.ConfigParser()
    config.read("/etc/keystone/keystone.conf")
    tls_enable_check_obj.read_tls_config(config)
