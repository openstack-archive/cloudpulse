from cloudpulse.scenario import base
from oslo_config import cfg
from oslo_utils import importutils
from cloudpulse.scenario.plugins.security_pulse.util.security_pulse_test_input import security_test_input_reader
from cloudpulse.scenario.plugins.security_pulse.util import security_pulse_test_util
from cloudpulse.scenario.plugins.security_pulse.testcase.tls_enable_test import tls_enablement_test
from cloudpulse.scenario.plugins.security_pulse.testcase.ks_admin_token_check import ks_admin_token_check
from cloudpulse.operator.ansible.openstack_node_info_reader import openstack_node_info_reader
from cloudpulse.operator.ansible.openstack_node import openstack_node_obj
import os
import cloudpulse


                   
TESTS_OPTS = [
    cfg.IntOpt('security_tls_enablement_check',
               default=0,
               help='TLS enablement check for keystone'),
    cfg.StrOpt('testcase_input_file',
               default='')
] 
                   
CONF = cfg.CONF

security_pulse_test_group = cfg.OptGroup(name='security_pulse_test',
                         title='Security pulse test param input file')                   
CONF.register_group(security_pulse_test_group)
CONF.register_opts(TESTS_OPTS,security_pulse_test_group)

class security_common_test(base.Scenario):

    def security_tls_enablement_check(self,*args,**kwargs):
    	testcase_input_file = cfg.CONF.security_pulse_test.testcase_input_file
        print testcase_input_file
        base_dir = os.path.dirname(cloudpulse.__file__)
    	testcase_input_file = base_dir+"/scenario/plugins/security_pulse/config/securityhealth_test_input.yaml"
    	input_reader = security_test_input_reader(testcase_input_file)
    	input_data = input_reader.process_security_input_file()
    	input_params = security_pulse_test_util.get_test_input_by_name("tls_enablement_check",input_data)
    	os_node_info_obj = openstack_node_info_reader(base_dir+"/scenario/plugins/security_pulse/config/openstack_config.yaml")
    	openstack_node_list = os_node_info_obj.get_host_list()
    	input_params['os_host_list'] = openstack_node_list
    	#print input_params
    	tls_test = tls_enablement_test()
    	result = tls_test.perform_tls_enablement_test(input_params)
    	print result
    	if result.startswith("Fail"):
    	    return (404, result,[])
        else:
    	    return (200, result,[])

    def security_keystone_admin_token_check(self,*args,**kwargs):
        #testcase_input_file = cfg.CONF.security_pulse_test.testcase_file
        base_dir = os.path.dirname(cloudpulse.__file__)
        testcase_input_file = base_dir+"/scenario/plugins/security_pulse/config/securityhealth_test_input.yaml"
        input_reader = security_test_input_reader(testcase_input_file)
        input_data = input_reader.process_security_input_file()
        input_params = security_pulse_test_util.get_test_input_by_name("ks_admin_token_check",input_data)
        os_node_info_obj = openstack_node_info_reader(base_dir+"/scenario/plugins/security_pulse/config/openstack_config.yaml")
        openstack_node_list = os_node_info_obj.get_host_list()
        input_params['os_host_list'] = openstack_node_list
        #print input_params
        ks_test = ks_admin_token_check()
        result = ks_test.perform_ks_admin_token_check_test(input_params)
        print result
        test_status = None
        data = ""
        for r in result:
            if test_status == None or r[2].startswith("Fail"):
                test_status="fail"
            elif test_status == None:
                test_status = "success"
            data = data + r[0]+" -> "+r[1]+" -> "+r[2]+"\n"
        if test_status == "fail":  
            return (404, data,[])
        else:
            return (200, data,[])


if __name__ == '__main__':
	sct = security_common_test()
	sct.security_tls_enablement_check()
