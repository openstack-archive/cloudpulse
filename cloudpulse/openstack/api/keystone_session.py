#    Copyright 2015 Rackspace
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from keystoneauth1.identity import v2 as v2_client
from keystoneauth1.identity import v3 as v3_client
from keystoneauth1 import session
from oslo_config import cfg
from oslo_log import log as logging
from oslo_utils import excutils

LOG = logging.getLogger(__name__)

cfg.CONF.import_group('keystone_authtoken', 'keystonemiddleware.auth_token')


def _get_kssession():
    kwargs = {'auth_url': cfg.CONF.keystone_authtoken.auth_uri,
              'username': cfg.CONF.keystone_authtoken.username,
              'password': cfg.CONF.keystone_authtoken.password}
    if cfg.CONF.keystone_authtoken.auth_uri[-3:] == '2.0':
        client = v2_client
        kwargs['tenant_name'] = cfg.CONF.keystone_authtoken.project_name
    elif cfg.CONF.keystone_authtoken.auth_uri[-1:] == '3':
        client = v3_client
        kwargs['project_name'] = cfg.CONF.keystone_authtoken.project_name
        kwargs['user_domain_id'] = cfg.CONF.keystone_authtoken.user_domain_id
        kwargs[
            'project_domain_id'] = (cfg.CONF.keystone_authtoken.
                                    project_domain_id)
    else:
        raise Exception('Unknown keystone version!')

    try:
        kc = client.Password(**kwargs)
        kssession = session.Session(
            auth=kc, verify=(cfg.CONF.keystone_authtoken.cafile))
        return kssession
    except Exception:
        with excutils.save_and_reraise_exception():
            LOG.exception("Error creating Keystone session.")
