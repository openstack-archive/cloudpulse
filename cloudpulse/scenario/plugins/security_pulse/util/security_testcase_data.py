class security_testcase(object):
    
    def __init__(self):
        self.test_name=None
        self.perform_on = []
        self.input_params = {}

    def get_test_name(self):
        return self.test_name
    
    def set_test_name(self,test_name):
        self.test_name = test_name
        
    def get_perform_on(self):
        return self.perform_on
    
    def set_perform_on(self,perform_on):
        self.perform_on = perform_on
    
    def get_input_params(self):
        return self.input_params
    
    def set_input_params(self,input_params):
        self.input_params = input_params
 
        
