class openstack_node_obj(object):
    
    def __init__(self,host,ip,user,password,role,name):
        self.host = host
        self.ip = ip
        self.user = user
        self.password = password
        self.role = role
        self.name = name

    def getHost(self):
        return self.host

    def getIp(self):
        return self.ip

    def getUser(self):
        return self.user

    def getPassword(self):
        return self.password

    def getRole(self):
        return self.role

    def getName(self):
        return self.name
