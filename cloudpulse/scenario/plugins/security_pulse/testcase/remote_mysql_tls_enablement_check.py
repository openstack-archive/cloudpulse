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
from pwd import getpwuid
import string


class mysql_tls_enable_check(object):

    def __init__(self):
        self.ssl_status = False
        self.SSL_file = '/etc/my.cnf.d/server.cnf'
        self.SSLOwner = 'mysql'
        self.config = ConfigParser.ConfigParser(allow_no_value=True)

    def getSSLStatus(self):
        ssl_files = []
        Result = {}
        final_result = {}
        overall_status = True
        if os.path.exists(self.SSL_file):
            try:
                self.config.read(self.SSL_file)
                self.ssl_status = self.config.get('mysqld', 'ssl')
                if self.ssl_status in ['true', 'True']:
                    ssl_files.append(self.config.get('mysqld', 'ssl-ca'))
                    ssl_files.append(self.config.get('mysqld', 'ssl-cert'))
                    ssl_files.append(self.config.get('mysqld', 'ssl-key'))
                    file_objs = self.getFileInfo(ssl_files)
                    if file_objs:
                        op = self.checkFilePermission(file_objs)
                        if op:
                            overall_status = False
                            final_result.update(
                                {'OverallStatus': overall_status})
                            Result.update(
                                {
                                    'Test Case Name': 'mysql TSL',
                                    'Message': 'SSL is enabled in mysql with \
                                     following mismatch - ' +
                                    string.join(
                                        op,
                                        ', '),
                                    'Status': 'Fail'})
                            final_result.update({'result': [Result]})
                            print (final_result)
                            return
                        else:
                            overall_status = True
                            final_result.update(
                                {'OverallStatus': overall_status})
                            Result.update({'Test Case Name': 'mysql TSL',
                                           'Message': 'SSL is enabled in \
                                           mysql',
                                           'Status': 'Pass'})
                            final_result.update({'result': [Result]})
                            print (final_result)
                            return
                    else:
                        overall_status = False
                        final_result.update({'OverallStatus': overall_status})
                        Result.update(
                            {
                                'Test Case Name': 'mysql TSL',
                                'Message': 'SSL is enabled in mysql and not \
                                able to check the file permission of \
                                SSL files',
                                'Status': 'Fail'})
                        final_result.update({'result': [Result]})
                        print (final_result)
                        return
                else:
                    overall_status = False
                    final_result.update({'OverallStatus': overall_status})
                    Result.update({'Test Case Name': 'mysql TSL',
                                   'Message': 'SSL is not enabled in mysql',
                                   'Status': 'Fail'})
                    final_result.update({'result': [Result]})
                    print (final_result)
                    return

            except Exception:
                overall_status = False
                final_result.update({'OverallStatus': overall_status})
                Result.update({'Test Case Name': 'mysql TSL',
                               'Message': 'Exception while \
                               reading ' + self.SSL_file,
                               'Status': 'Fail'})
                final_result.update({'result': [Result]})
                print (final_result)
                return
        else:
            overall_status = False
            final_result.update({'OverallStatus': overall_status})
            Result.update({'Test Case Name': 'mysql TSL',
                           'Message': self.SSL_file + ' not found',
                           'Status': 'Fail'})
            final_result.update({'result': [Result]})
            print (final_result)
            return

    def formfileObj(self, file_name, stat_file_obj):
        file_info = {}
        try:
            file_info['owner'] = getpwuid(stat_file_obj.st_uid).pw_name
            file_info['group_owner'] = getpwuid(stat_file_obj.st_gid).pw_name
        except Exception:
            pass
        return file_info

    def getFileInfo(self, files=[]):
        file_objs = {}
        try:
            for f in files:
                obj = os.stat(f)
                opt = self.formfileObj(f, obj)
                file_objs.update({f: opt})
        except Exception:
            pass
        return file_objs

    def checkFilePermission(self, file_objs={}):
        result = []
        for file, obj in file_objs.items():
            if obj.get('owner') != self.SSLOwner:
                msg = 'File "%s" owner permission is not matching' % (file)
                result.append(msg)
            if obj.get('group_owner') != self.SSLOwner:
                msg = 'File "%s" group owner permision is not matching' % (
                    file)
                result.append(msg)
        return result


if __name__ == '__main__':
    checkssl = mysql_tls_enable_check()
    checkssl.getSSLStatus()
