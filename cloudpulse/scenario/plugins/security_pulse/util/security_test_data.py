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


class security_test(object):

    def __init__(self):
        self.test_name = None
        self.security_testcase = []
        self.perform_on = []
        self.test_to_execute = []

    def get_test_name(self):
        return self.test_name

    def get_security_testcase(self):
        return self.security_testcase

    def set_test_name(self, test_name):
        self.test_name = test_name

    def set_security_testcase(self, security_testcase):
        self.security_testcase = security_testcase

    def get_perform_on(self):
        return self.perform_on

    def set_perform_on(self, perform_on):
        self.perform_on = perform_on

    def get_test_to_execute(self):
        return self.test_to_execute

    def set_test_to_execute(self, test_to_execute):
        self.test_to_execute = test_to_execute
