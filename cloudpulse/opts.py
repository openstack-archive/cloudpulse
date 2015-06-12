# Copyright 2014
# The Cloudscaling Group, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import itertools

import cloudpulse.api.app
import cloudpulse.api.auth
import cloudpulse.common.clients
import cloudpulse.common.cloudpulse_keystoneclient
import cloudpulse.common.exception
import cloudpulse.conductor.config
import cloudpulse.db.sqlalchemy.models
import cloudpulse.openstack.common.eventlet_backdoor
import cloudpulse.openstack.common.log
import cloudpulse.openstack.common.periodic_task


def list_opts():
    return [
        ('DEFAULT',
         itertools.chain(cloudpulse.api.auth.AUTH_OPTS,
                         cloudpulse.common.cloudpulse_keystoneclient.topts,
                         cloudpulse.common.paths.PATH_OPTS,
                         cloudpulse.common.utils.UTILS_OPTS,
                         (cloudpulse.openstack.common.eventlet_backdoor
                          .eventlet_backdoor_opts),
                         cloudpulse.openstack.common.log.generic_log_opts,
                         cloudpulse.openstack.common.log.log_opts,
                         cloudpulse.openstack.common.log.common_cli_opts,
                         cloudpulse.openstack.common.log.logging_cli_opts,
                         cloudpulse.openstack.common.periodic_task.popts,
                         )),
        ('api', cloudpulse.api.app.API_SERVICE_OPTS),
        ('conductor', cloudpulse.conductor.config.SERVICE_OPTS),
        ('database', cloudpulse.db.sqlalchemy.models.sql_opts),
    ]
