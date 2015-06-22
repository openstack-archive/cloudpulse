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

from keystoneclient.exceptions import ClientException
from keystoneclient.v2_0 import client as keystone_client


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
        return (self.keystoneclient
                .service_catalog.url_for(
                    service_type=service_type,
                    endpoint_type=endpoint_type))

    def keystone_return_authtoken(self):
        return self.keystoneclient.auth_token

    def _get_admin_user_id(self, admin_user):
        try:
            user_list = self.keystoneclient.users.list()
            for user in user_list:
                if user.name == admin_user:
                    return(200, "success", user.id)
        except(ClientException, Exception) as e:
            return (404, e.message, [])
        return (404, "User not avaiable Failure", [])

    def _get_admin_role_id(self, admin_role):
        try:
            role_list = self.keystoneclient.roles.list()
            for role in role_list:
                if role.name == admin_role:
                    return(200, "success", role.id)
        except(ClientException, Exception) as e:
            return (404, e.message, [])
        return (404, "Role not avaiable Failure", [])

    def keystone_tenant_create(self, tenant):
        try:
            tenant_res = self.keystoneclient.tenants.create(tenant_name=tenant,
                                                            enabled=True)
            self._role_assign(tenant_res)
        except (ClientException, Exception) as e:
            return (404, e.message, [])
        return (200, "success", tenant_res)

    def _role_assign(self, tenant, role="admin", user="admin"):
        role = self._get_admin_role_id("admin")[2]
        user = self._get_admin_user_id("admin")[2]
        self.keystoneclient.roles.add_user_role(user,
                                                role,
                                                tenant.id)

    def keystone_tenant_delete(self, tenant_id):
        try:
            tenant_res = self.keystoneclient.tenants.delete(tenant_id)
        except (ClientException, Exception) as e:
            return (404, e.message, [])
        return (200, "success", tenant_res)
