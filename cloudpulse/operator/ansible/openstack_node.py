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


class openstack_node_obj(object):
    def __init__(self, host, ip, user, password, role, name):
        self.host = host
        self.ip = ip
        self.user = user
        self.password = password
        self.role = role
        self.name = name

    def getHost(self):
        return self.host

    def getIp(self):
        return self.ip

    def getUser(self):
        return self.user

    def getPassword(self):
        return self.password

    def getRole(self):
        return self.role

    def getName(self):
        return self.name
