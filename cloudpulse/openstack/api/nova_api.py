from novaclient.client import Client
from novaclient.exceptions import ClientException
class NovaHealth(object):
    """
    Provides all the necessary API
    for nova health Check
    """
    def __init__(self, creden):
        creden['timeout'] = 30
        self.novaclient = Client(**creden)
    
    def nova_service_list(self):
        """
        Get the list of nova services
        """
        try:
            service_list = self.novaclient.services.list()
        except (ClientException, Exception) as e:
            return (400, e.message, [])
        return (200, "success", service_list)

    def nova_create_server(self,server_name,image_name,flavor_name,network_id):
        try:
            image = self.novaclient.images.find(name=image_name)
            flavor = self.novaclient.flavors.find(name=flavor_name)
            networks = [{'net-id': network_id}]
            server_ret = self.novaclient.servers.create(server_name,image,flavor,nics=networks)
        except (ClientException, Exception) as e:
            return (400, e.message, [])
        return (200, "success", server_ret)

    def nova_delete_server(self,server_id):
        try:
            ret = self.novaclient.servers.delete(server_id)
        except (ClientException, Exception) as e:
            return (400, e.message, [])
        return (200, "success", ret)

    def nova_get_server_state(self,server_id):
        try:
            ret = self.novaclient.servers.get(server_id)
        except (ClientException, Exception) as e:
            return (400, e.message, [])
        return (200, "success", ret)

    def nova_attach_volume(self,server_id,volume_id):
        try:
            ret = self.novaclient.volumes.create_server_volume(server_id, volume_id, "/dev/vdb")
        except (ClientException, Exception) as e:
            return (400, e.message, [])
        return (200, "success", ret)

    def nova_detach_volume(self,server_id,attachment_id):
        try:
            ret = self.novaclient.volumes.delete_server_volume(server_id, attachment_id)
        except (ClientException, Exception) as e:
            return (400, e.message, [])
        return (200, "success", ret)

