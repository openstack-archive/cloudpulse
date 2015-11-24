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


class password_encryption_test(object):

    def password_encryption_check(self, config):
        overall_status = True
        final_result = {}
        Result = {}
        try:
            config.get("token", "hash_algorithm")
        except ConfigParser.NoOptionError:
            overall_status = False
            final_result.update({'OverallStatus': overall_status})
            msg = {
                'test_case_name': 'Hash Algorithm',
                'message': 'Hash Algorithm option is commented',
                'status': 'Fail'}
            Result.update(msg)
            final_result.update({'result': [Result]})
            print (final_result)
            return
        else:
            algo = config.get("token", "hash_algorithm")
            if algo == "sha1" or algo == "sha256":
                try:
                    config.get("token", "provider")
                except ConfigParser.NoOptionError:
                    overall_status = False
                    final_result.update({'OverallStatus': overall_status})
                    msg = {
                        'test_case_name': 'Provider option',
                        'message': 'Provider option is not enabled',
                        'status': 'Fail'}
                    Result.update(msg)
                    final_result.update({'result': [Result]})
                    print (final_result)
                    return
                else:
                    provider = config.get("token", "provider")
                    if provider == "pki":
                        final_result.update({'OverallStatus': overall_status})
                        msg = {
                            'test_case_name': 'Provider option',
                            'message': "hash algorithm option enabled " +
                            " with value " +
                            algo +
                            " and provider " +
                            "using 'pki' ",
                            'status': 'Pass'}
                        Result.update(msg)
                        final_result.update({'result': [Result]})
                        print (final_result)
                        return
                    elif provider == "uuid":
                        overall_status = False
                        final_result.update({'OverallStatus': overall_status})
                        msg = {
                            'test_case_name': 'Provider option',
                            'message': "hash algorithm option enabled " +
                            " with value " +
                            algo +
                            " and provider " +
                            "using 'uuid' ",
                            'status': 'Fail'}
                        Result.update(msg)
                        final_result.update({'result': [Result]})
                        print (final_result)
                        return
            elif algo == "md5":
                overall_status = False
                final_result.update({'OverallStatus': overall_status})
                msg = {
                    'test_case_name': 'Provider option',
                    'message': "hash algorithm option enabled " +
                    " with value " +
                    algo,
                    'status': 'Fail'}
                Result.update(msg)
                final_result.update({'result': [Result]})
                print (final_result)
                return

if __name__ == '__main__':
    pet = password_encryption_test()
    config = ConfigParser.ConfigParser()
    config.read("/etc/keystone/keystone.conf")
    pet.password_encryption_check(config)
