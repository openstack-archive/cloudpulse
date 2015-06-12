#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""API for interfacing with Magnum Backend."""
from oslo_config import cfg

from cloudpulse.common import rpc_service
from cloudpulse import objects


# The Backend API class serves as a AMQP client for communicating
# on a topic exchange specific to the conductors.  This allows the ReST
# API to trigger operations on the conductors

class API(rpc_service.API):
    def __init__(self, transport=None, context=None, topic=None):
        if topic is None:
            cfg.CONF.import_opt('topic', 'cloudpulse.conductor.config',
                                group='conductor')
        super(API, self).__init__(transport, context,
                                  topic=cfg.CONF.conductor.topic)

    # Test Operations
    def test_create(self, test, cpulse_create_timeout):
        # TODO(RPC CALL)
        # return self._call('cpulse_create', test=test, cpulse_create_timeout)
        test.create(cpulse_create_timeout)
        return test

    def test_list(self, context, limit, marker, sort_key, sort_dir):
        return objects.Cpulse.list(context, limit, marker, sort_key, sort_dir)

    def test_delete(self, context, uuid):
        # return self._call('cpulse_delete', uuid=uuid)
        test = objects.Cpulse.get_by_uuid(context, uuid=uuid)
        return test.destroy()

    def test_show(self, context, uuid):
        return objects.Cpulse.get_by_uuid(context, uuid)

    def test_update(self, test):
        return self._call('cpulse_update', test=test)


class ListenerAPI(rpc_service.API):
    def __init__(self, context=None, topic=None, server=None, timeout=None):
        super(ListenerAPI, self).__init__(context=context, topic=topic,
                                          server=server, timeout=timeout)

    def ping_conductor(self):
        return self._call('ping_conductor')
