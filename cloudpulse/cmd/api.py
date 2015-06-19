# Copyright 2013 - Red Hat, Inc.
#
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

"""Starter script for the Cloudpulse API service."""

import logging as std_logging
import os
import sys
from wsgiref import simple_server

from oslo_config import cfg

from cloudpulse.api import app as api_app
from cloudpulse.common import service
from cloudpulse.openstack.common._i18n import _LI
from cloudpulse.openstack.common import log as logging


LOG = logging.getLogger(__name__)


def main():
    service.prepare_service(sys.argv)

    app = api_app.setup_app()

    # Create the WSGI server and start it
    host, port = cfg.CONF.host, cfg.CONF.port
    srv = simple_server.make_server(host, port, app)

    LOG.info(_LI('Starting server in PID %s') % os.getpid())
    LOG.debug("Configuration:")
    cfg.CONF.log_opt_values(LOG, std_logging.DEBUG)

    if host == '0.0.0.0':
        LOG.info(_LI('serving on 0.0.0.0:%(port)s, '
                   'view at http://127.0.0.1:%(port)s') %
                 dict(port=port))
    else:
        LOG.info(_LI('serving on http://%(host)s:%(port)s') %
                 dict(host=host, port=port))

    srv.serve_forever()
