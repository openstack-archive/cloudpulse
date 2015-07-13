class security_test(object):
    
    def __init__(self):
        self.test_name=None
        self.security_testcase = []
        self.perform_on = []
        self.test_to_execute = []
    
    def get_test_name(self):
        return self.test_name

    def get_security_testcase(self):
        return self.security_testcase
    
    def set_test_name(self,test_name):
        self.test_name = test_name

    def set_security_testcase(self,security_testcase):
        self.security_testcase = security_testcase
    
    def get_perform_on(self):
        return self.perform_on
    
    def set_perform_on(self,perform_on):
        self.perform_on = perform_on

    def get_test_to_execute(self):
        return self.test_to_execute
    
    def set_test_to_execute(self,test_to_execute):
        self.test_to_execute = test_to_execute
