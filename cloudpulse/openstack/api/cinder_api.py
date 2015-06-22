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

from cinderclient.client import Client


class CinderHealth(object):
    def __init__(self, creds):
        self.cinderclient = Client(**creds)

    def cinder_list(self):
        try:
            cinder_list = self.cinderclient.volumes.list()
        except Exception as e:
            return (404, e.message, [])
        return (200, "success", cinder_list)

    def cinder_volume_create(self, volume_name, volume_size):
        try:
            cinder_ret = self.cinderclient.volumes.create(volume_size,
                                                          name=volume_name)
        except Exception as e:
            return (404, e.message, [])
        return (200, "success", cinder_ret)

    def cinder_volume_delete(self, volume_id):
        try:
            cinder_ret = self.cinderclient.volumes.delete(volume_id)
        except Exception as e:
            return (404, e.message, [])
        return (200, "success", cinder_ret)
