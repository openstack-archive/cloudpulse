from neutronclient.v2_0 import client as neutron_client
from neutronclient.common.exceptions import NeutronException
class NeutronHealth(object):
    def __init__(self, creds):
        creds['timeout'] = 30
        self.neutronclient = neutron_client.Client(**creds)
    
    def neutron_agent_list(self):
        try:
            agent_list = self.neutronclient.list_agents()  
        except (NeutronException,Exception) as e:
            return (404, e.message, [])
        return (200, "success", agent_list['agents'])

    def network_create(self,network_name):
        try:
            self.neutronclient.format = 'json'
            network = {'name': network_name, 'admin_state_up': True}
            res = self.neutronclient.create_network({'network':network})
        except (NeutronException, Exception) as e:
            return (404, e.message, [])
        return (200, "success",res )

    def subnet_create(self,network_id,network_cidr):
        try:
            self.neutronclient.format = 'json'
            subnet = {
                                 "name" : "cpulse_test",
                                 "network_id": network_id,
                                 "ip_version": 4,
                                 "cidr": network_cidr
                     }
            res = self.neutronclient.create_subnet({'subnet' : subnet })
        except (NeutronException, Exception) as e:
            return (404, e.message, [])
        return (200, "success",res )

    def network_delete(self,network_id):
        try:
            self.neutronclient.format = 'json'
            network = {'id': network_id}
            res = self.neutronclient.delete_network(network_id)
        except (NeutronException, Exception) as e:
            return (404, e.message, [])
        return (200, "success",res )
