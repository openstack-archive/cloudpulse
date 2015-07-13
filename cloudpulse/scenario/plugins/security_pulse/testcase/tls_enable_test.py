import os
#from tabulate import tabulate
from cloudpulse.operator.ansible.ansible_runner import ansible_runner
import cloudpulse

TMP_LOCATION = "/tmp/sec_hc/"

class tls_enablement_test(object):

	def perform_tls_enablement_test(self,input_params):
		
		print "Executing the test "+input_params.get('testcase_name')

		file_info_dir = input_params['global_data']['file_info_dir']
		perform_on = input_params['perform_on']
		if perform_on == None or not perform_on:
			print "Perform on should be mentioned either at test level or test case level"
			return
		os_hostobj_list = input_params['os_host_list']
		base_dir = os.path.dirname(cloudpulse.__file__)
		flist=[base_dir+"/scenario/plugins/security_pulse/testcase/TLS_Enablement_Check.py"]
        #print os_hostobj_list
		ans_runner = ansible_runner(os_hostobj_list)
		ans_runner.execute_cmd("python "+TMP_LOCATION+"TLS_Enablement_Check.py "+TMP_LOCATION,file_list=flist)
		result = ans_runner.get_results()

		#files = os.walk(file_info_dir+'output/').next()[1]
		#report_objs = self.consolidate_report_objs(file_info_dir,files)
		#headers = ['Status','Description']
		os.system('rm -rf '+file_info_dir+'output')
		for key in result.keys():
			return result[key]

	
	"""
	def display_to_terminal(self,output,headers):
		print tabulate(output,headers,tablefmt="grid")
	"""
	
	def consolidate_report_objs(self,file_info_dir,files=[],root_path='/tmp/sec_hc/output'):
		consolidated_objs = []
		obj = {}
		for f in files:
			str = open(file_info_dir+'output/'+f+root_path,'r').read()
			obj['result'] = str 
			consolidated_objs.append(obj)
		return consolidated_objs
