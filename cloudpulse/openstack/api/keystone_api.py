from keystoneclient.v2_0 import client as keystone_client
from keystoneclient.exceptions import ClientException

class KeystoneHealth(object):
    def __init__(self, creds):
        self.keystoneclient = keystone_client.Client(**creds)
    
    def keystone_service_list(self):
        try:
            service_list = self.keystoneclient.services.list()
        except (ClientException, Exception) as e:
            return (404, e.message, [])
        return (200, "success", service_list)
    
    def keystone_endpoint_find(self, service_type, endpoint_type='publicURL'):
        return self.keystoneclient.service_catalog.url_for(service_type=service_type, endpoint_type=endpoint_type)
    
    def keystone_return_authtoken(self):
        return self.keystoneclient.auth_token

    def _get_admin_user_id(self,admin_user):
        try:
            user_list = self.keystoneclient.users.list()
            for user in user_list:
                if user.name == admin_user:
                    return(200,"success",user.id)
        except(ClientException, Exception) as e:
            return (404, e.message, [])
        return (404, "User not avaiable Failure",[] )

    def _get_admin_role_id(self,admin_role):
        try:
            role_list = self.keystoneclient.roles.list()
            for role in role_list:
                if role.name == admin_role:
                    return(200,"success",role.id)
        except(ClientException, Exception) as e:
            return (404, e.message, [])
        return (404, "Role not avaiable Failure",[] )

    def keystone_tenant_create(self,tenant_name):
        try:
            tenant_res = self.keystoneclient.tenants.create(tenant_name=tenant_name,enabled=True)
            self._role_assign(tenant_res)
        except (ClientException, Exception) as e:
            return (404, e.message, [])
        return (200, "success",tenant_res )

    def _role_assign(self,tenant_name,role="admin",user="admin"):
        role = self._get_admin_role_id("admin")[2]
        user = self._get_admin_user_id("admin")[2]
        role_assign_res = self.keystoneclient.roles.add_user_role(user,role,tenant_name.id)

    def keystone_tenant_delete(self,tenant_id):
        try:
            tenant_res = self.keystoneclient.tenants.delete(tenant_id)
        except (ClientException, Exception) as e:
            return (404, e.message, [])
        return (200, "success",tenant_res )
