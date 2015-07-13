import os
from cloudpulse.operator.ansible.ansible_runner import ansible_runner
import cloudpulse

TMP_LOCATION = "/tmp/sec_hc/"

class ks_admin_token_check(object):

	def perform_ks_admin_token_check_test(self,input_params):
		print "Executing the test "+input_params.get('testcase_name')
		file_info_dir = input_params['global_data']['file_info_dir']
		perform_on = input_params['perform_on']
		if perform_on == None or not perform_on:
			print "Perform on should be mentioned either at test level or test case level"
			return
		os_hostobj_list = input_params['os_host_list']
		base_dir = os.path.dirname(cloudpulse.__file__)
		flist=[base_dir+"/scenario/plugins/security_pulse/testcase/keystone_admin_token_check.py"]
		ans_runner = ansible_runner(os_hostobj_list)
		ans_runner.execute_cmd("python "+TMP_LOCATION+"keystone_admin_token_check.py "+TMP_LOCATION,file_list=flist)
		result = ans_runner.get_results()
		result_row = []
		for key in result.keys():
			obj = eval(result[key])
			for r in obj:
				result = r.split(" - ")
				result_row.append([result[0],result[1],result[2]])
		os.system('rm -rf '+file_info_dir+'output')
		return result_row

		"""
		files = os.walk(file_info_dir+'output/').next()[1]
		result_row = []
		for f in files:
			obj = eval(open('/tmp/sec_hc/output/'+f+'/tmp/sec_hc/output','r').read())
			for r in obj:
				result = r.split(" - ")
				result_row.append([result[0],result[1],result[2]])
		os.system('rm -rf '+file_info_dir+'output')
		return result_row
		"""
