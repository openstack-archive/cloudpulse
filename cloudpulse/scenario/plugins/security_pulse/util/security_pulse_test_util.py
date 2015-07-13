def get_test_input_by_name(testcase_name,input_data):
	sec_test_lst = input_data['sec_test_lst']
	for test_obj in sec_test_lst:
		for test_case_obj in test_obj.get_security_testcase():
			if testcase_name == test_case_obj.get_test_name():
				input_params = test_case_obj.get_input_params()
				input_params['testcase_name'] = testcase_name
				if test_case_obj.get_perform_on() is not None:
					input_params['perform_on'] = test_case_obj.get_perform_on()
				else:
					input_params['perform_on'] = test_obj.get_perform_on()
				input_params['test_name'] = test_obj.get_test_name()
				input_params['global_data'] = input_data['global_data']
				return input_params
	return None




