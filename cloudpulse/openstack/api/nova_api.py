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

from novaclient.client import Client
from novaclient.exceptions import ClientException


class NovaHealth(object):
    def __init__(self, creden):
        creden['timeout'] = 30
        self.novaclient = Client(**creden)

    def nova_service_list(self):
        try:
            service_list = self.novaclient.services.list()
        except (ClientException, Exception) as e:
            return (400, e.message, [])
        return (200, "success", service_list)

    def nova_create_server(self, server_name, image_name,
                           flavor_name, network_id):
        try:
            image = self.novaclient.images.find(name=image_name)
            flavor = self.novaclient.flavors.find(name=flavor_name)
            networks = [{'net-id': network_id}]
            server_ret = self.novaclient.servers.create(server_name, image,
                                                        flavor, nics=networks)
        except (ClientException, Exception) as e:
            return (400, e.message, [])
        return (200, "success", server_ret)

    def nova_delete_server(self, server_id):
        try:
            ret = self.novaclient.servers.delete(server_id)
        except (ClientException, Exception) as e:
            return (400, e.message, [])
        return (200, "success", ret)

    def nova_get_server_state(self, server_id):
        try:
            ret = self.novaclient.servers.get(server_id)
        except (ClientException, Exception) as e:
            return (400, e.message, [])
        return (200, "success", ret)

    def nova_attach_volume(self, server_id, volume_id):
        try:
            ret = self.novaclient.volumes.create_server_volume(server_id,
                                                               volume_id,
                                                               "/dev/vdb")
        except (ClientException, Exception) as e:
            return (400, e.message, [])
        return (200, "success", ret)

    def nova_detach_volume(self, server_id, attachment_id):
        try:
            ret = self.novaclient.volumes.delete_server_volume(server_id,
                                                               attachment_id)
        except (ClientException, Exception) as e:
            return (400, e.message, [])
        return (200, "success", ret)
