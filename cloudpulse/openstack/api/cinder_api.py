from cinderclient.client import Client
import time
import credentials

class CinderHealth(object):
    def __init__(self, creds):
        self.cinderclient = Client(**creds)
    
    def cinder_list(self):
        try:
            cinder_list = self.cinderclient.volumes.list()
        except Exception as e:
            return (404, e.message, [])
        return (200, "success" , cinder_list)

    def cinder_volume_create(self,volume_name,volume_size):
        try:
            cinder_ret = self.cinderclient.volumes.create(volume_size,name=volume_name)
        except Exception as e:
            return (404, e.message, [])
        return (200, "success" , cinder_ret)
    
    def cinder_volume_delete(self,volume_id):
        try:
            cinder_ret = self.cinderclient.volumes.delete(volume_id)
        except Exception as e:
            return (404, e.message, [])
        return (200, "success" , cinder_ret)

