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


class security_testcase(object):

    def __init__(self):
        self.test_name = None
        self.perform_on = []
        self.input_params = {}

    def get_test_name(self):
        return self.test_name

    def set_test_name(self, test_name):
        self.test_name = test_name

    def get_perform_on(self):
        return self.perform_on

    def set_perform_on(self, perform_on):
        self.perform_on = perform_on

    def get_input_params(self):
        return self.input_params

    def set_input_params(self, input_params):
        self.input_params = input_params
