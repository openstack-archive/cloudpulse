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

from cloudpulse.scenario.plugins.security_pulse.util.security_test_data \
    import security_test
from cloudpulse.scenario.plugins.security_pulse.util.security_testcase_data \
    import security_testcase
import yaml


class security_test_input_reader(object):

    def __init__(self, fileName):
        self.secInputYamlObj = None
        self.security_tests = []
        try:
            fp = open(fileName)
        except IOError as e:
            print ("Error while opening the file...%s", e)
            return

        try:
            self.secInputYamlObj = yaml.load(fp)
        except yaml.error.YAMLError as perr:
            print ("Error while parsing...%s", perr)
            return

    def process_security_input_file(self):
        # print self.secInputYamlObj
        secTests = self.secInputYamlObj["securityhealth"]
        globalVarData = {}
        input_data = {}
        sec_test_lst = []
        for test_key in secTests.keys():
            if test_key == "global_data":
                for gkey in secTests[test_key].keys():
                    globalVarData[gkey] = secTests[test_key][gkey]
                continue
            sec_test_obj = security_test()
            sec_test_obj.set_test_name(test_key)
            sec_test_case_lst = []
            test_data = secTests[test_key]
            for test_case_key in test_data.keys():
                if test_case_key == "perform_on":
                    sec_test_obj.set_perform_on(secTests[test_key]
                                                [test_case_key])
                elif test_case_key == "testcase":
                    sec_test_obj.set_test_to_execute(secTests[test_key]
                                                     [test_case_key])
                else:
                    security_testcase_obj = security_testcase()
                    security_testcase_obj.set_test_name(test_case_key)
                    if "perform_on" in secTests[test_key][test_case_key]:
                        # print secTests[test_key][test_case_key]["perform_on"]
                        security_testcase_obj.\
                            set_perform_on(secTests[test_key]
                                           [test_case_key]
                                           ["perform_on"])
                    test_input_dict = {}
                    if "input" in secTests[test_key][test_case_key]:
                        if secTests[test_key][test_case_key]["input"] \
                            is not None:
                            for test_case_input_key in \
                                secTests[test_key][test_case_key]["input"].\
                                    keys():
                                test_input_dict[test_case_input_key] = \
                                    (secTests[test_key][test_case_key]["input"]
                                     [test_case_input_key])
                        security_testcase_obj.\
                            set_input_params(test_input_dict)
                        sec_test_case_lst.append(security_testcase_obj)
                    else:
                        sec_test_case_lst = sec_test_case_lst + \
                            self.process_testcase_input(test_key,
                                                        test_case_key,
                                                        secTests)
            sec_test_obj.set_security_testcase(sec_test_case_lst)
            sec_test_lst.append(sec_test_obj)
        # security_test_input_reader.print_test_input(sec_test_lst)
        # print globalVarData
        input_data['global_data'] = globalVarData
        input_data['sec_test_lst'] = sec_test_lst
        return input_data

    def process_testcase_input(self, test_key, test_case_key, secTests):
        sec_test_case_lst = []
        # print secTests[test_key][test_case_key]
        for sub_test_case_key in (secTests[test_key]
                                  [test_case_key]).keys():
            security_testcase_obj = security_testcase()
            security_testcase_obj.set_test_name(test_case_key + "." +
                                                sub_test_case_key)
            if "perform_on" in (secTests[test_key][test_case_key]
                                [sub_test_case_key]):
                security_testcase_obj.\
                    set_perform_on(secTests[test_key][test_case_key]
                                   [sub_test_case_key]["perform_on"])
            if "input" in secTests[test_key][test_case_key][sub_test_case_key] \
                and (secTests[test_key][test_case_key][sub_test_case_key]
                     ["input"]) is not None:
                test_input_dict = {}
                for test_case_input_key in \
                    (secTests[test_key][test_case_key]
                     [sub_test_case_key]["input"]).keys():
                    test_input_dict[test_case_input_key] = \
                        (secTests[test_key][test_case_key]
                         [sub_test_case_key]["input"][test_case_input_key])
                security_testcase_obj.set_input_params(test_input_dict)
            sec_test_case_lst.append(security_testcase_obj)
        return sec_test_case_lst

    """
    @staticmethod
    def print_test_input(sec_test_lst):
        for test_obj in sec_test_lst:
            print "TestName        : %s " % test_obj.get_test_name()
            print "Perform On      : %s " % test_obj.get_perform_on()
            print "Test to execute : %s " % test_obj.get_test_to_execute()
            for test_case_obj in test_obj.get_security_testcase():
                print "     Test case Name : %s " % test_case_obj.\
                    get_test_name()
                print "     Perform On     : %s " % test_case_obj.\
                    get_perform_on()
                print "     Input Params   : %s " % test_case_obj.\
                    get_input_params()
    """

if __name__ == '__main__':
    yhp = security_test_input_reader()
    yhp.process_security_input_file()
