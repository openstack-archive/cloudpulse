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


class keystone_admin_token_check(object):
    def __init__(self):
        pass

    def keystone_admin_token_test(self):
        ks_conf_file = "/etc/keystone/keystone.conf"
        result = []
        config = ConfigParser.ConfigParser()
        if os.path.exists(ks_conf_file):
            try:
                config.read(ks_conf_file)
            except Exception:
                result.append("admin_token - keystone.conf not found - Fail")
            else:
                try:
                    config.get("DEFAULT", "admin_token")
                except ConfigParser.NoOptionError:
                    result.append("admin_token - Not defined - Pass")
                else:
                    result.append("admin_token - Defined - Fail")
        else:
            result.append("admin_token - keystone.conf not found - Fail")

        ks_paste_conf_file = "/etc/keystone/keystone-paste.ini"
        if os.path.exists(ks_paste_conf_file):
            try:
                config.read(ks_paste_conf_file)
            except Exception:
                result.append("admin_auth_token - keystone-paste.ini not " +
                              "found - Pass")
            else:
                try:
                    config.get("filter:admin_token_auth",
                               "paste.filter_factory")
                except (ConfigParser.NoOptionError,
                        ConfigParser.NoSectionError):
                    result.append("admin_auth_token - Not defined - Pass")
                else:
                    option = config.get("filter:admin_token_auth",
                                        "paste.filter_factory")
                    if "AdminTokenAuthMiddleware" in option:
                        result.append("admin_auth_token - Defined - Fail")
                    else:
                        result.append("admin_auth_token - Not Defined - Pass")
        else:
            result.append("admin_auth_token - keystone-paste.ini not found " +
                          "- Pass")
        print (result)

if __name__ == '__main__':
    keystone_admin_token_check_obj = keystone_admin_token_check()
    keystone_admin_token_check_obj.keystone_admin_token_test()
