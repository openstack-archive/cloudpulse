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


class HostObject(object):

    def __init__(self, host, ip, user, role, name, isNagios=False):
        self.host = host
        self.ip = ip
        self.user = user
        self.isNagios = isNagios
        self.role = role
        self.name = name
        self.dirlist = []

    def setNagios(self, isNagios):
        self.isNagios = isNagios

    def isNagiosRunning(self):
        return self.isNagios

    def getHost(self):
        return self.host

    def getIp(self):
        return self.ip

    def getUser(self):
        return self.user

    def getRole(self):
        return self.role

    def getName(self):
        return self.name

    def setDirList(self, dir_list):
        self.dirlist = dir_list

    def getDirList(self):
        return self.dirlist
