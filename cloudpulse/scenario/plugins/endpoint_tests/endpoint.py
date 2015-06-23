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

from cloudpulse.openstack.api.cinder_api import CinderHealth
from cloudpulse.openstack.api.glance_api import GlanceHealth
from cloudpulse.openstack.api.keystone_api import KeystoneHealth
from cloudpulse.openstack.api.neutron_api import NeutronHealth
from cloudpulse.openstack.api.nova_api import NovaHealth
from cloudpulse.scenario import base
from oslo_config import cfg
from oslo_utils import importutils

cfg.CONF.import_opt('auth_uri', 'keystonemiddleware.auth_token',
                    group='keystone_authtoken')

TESTS_OPTS = [
    cfg.IntOpt('nova_endpoint',
               default=0,
               help='The nova endpoint and interval'),
    cfg.IntOpt('neutron_endpoint',
               default=0,
               help='The neutron endpoint and interval'),
    cfg.IntOpt('keystone_endpoint',
               default=0,
               help='The keystone endpoint and interval'),
    cfg.IntOpt('glance_endpoint',
               default=0,
               help='The glance endpoint and interval'),
    cfg.IntOpt('cinder_endpoint',
               default=0,
               help='The cinder endpoint and interval')
]

CONF = cfg.CONF

periodic_test_group = cfg.OptGroup(name='periodic_tests',
                                   title='Periodic tests to be run')
CONF.register_group(periodic_test_group)
CONF.register_opts(TESTS_OPTS, periodic_test_group)


class endpoint_scenario(base.Scenario):
    def _get_credentials(self):
        importutils.import_module('keystonemiddleware.auth_token')
        creds = {}
        creds['username'] = cfg.CONF.keystone_authtoken.username
        creds['tenant_name'] = cfg.CONF.keystone_authtoken.project_name
        creds['password'] = cfg.CONF.keystone_authtoken.password
        creds['auth_url'] = cfg.CONF.keystone_authtoken.auth_uri
        return creds

    def _get_nova_v2_credentials(self):
        importutils.import_module('keystonemiddleware.auth_token')
        creds = {}
        creds['username'] = cfg.CONF.keystone_authtoken.username
        creds['project_id'] = cfg.CONF.keystone_authtoken.project_name
        creds['api_key'] = cfg.CONF.keystone_authtoken.password
        creds['auth_url'] = cfg.CONF.keystone_authtoken.auth_uri
        creds['version'] = 2
        return creds

    @base.scenario(admin_only=False, operator=False)
    def nova_endpoint(self, *args, **kwargs):
        creds = self._get_nova_v2_credentials()
        nova = NovaHealth(creds)
        return nova.nova_service_list()

    @base.scenario(admin_only=False, operator=False)
    def neutron_endpoint(self, *args, **kwargs):
        creds = self._get_credentials()
        neutron = NeutronHealth(creds)
        return neutron.neutron_agent_list()

    @base.scenario(admin_only=False, operator=False)
    def keystone_endpoint(self, *args, **kwargs):
        creds = self._get_credentials()
        keystone = KeystoneHealth(creds)
        return keystone.keystone_service_list()

    @base.scenario(admin_only=False, operator=False)
    def glance_endpoint(self, *args, **kwargs):
        creds = self._get_credentials()
        keystone = KeystoneHealth(creds)
        glance = GlanceHealth(keystone)
        return glance.glance_image_list()

    @base.scenario(admin_only=False, operator=False)
    def cinder_endpoint(self, *args, **kwargs):
        creds = self._get_nova_v2_credentials()
        cinder = CinderHealth(creds)
        return cinder.cinder_list()
