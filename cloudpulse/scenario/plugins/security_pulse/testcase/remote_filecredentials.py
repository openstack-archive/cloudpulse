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


class AccessPreveliges(object):

    def __init__(self, name=None, size=None, mode=None, user=None, group=None):
        self.name = name
        self.size = str(size)
        self.mode = mode
        self.user = user
        self.group = group

    def getName(self):
        return self.name

    def getSize(self):
        return self.size

    def getMode(self):
        return self.mode

    def getUser(self):
        return self.user[0]

    def getGroup(self):
        return self.group[0]
