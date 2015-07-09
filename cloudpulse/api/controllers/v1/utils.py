# Copyright 2013 Red Hat, Inc.
# All Rights Reserved.
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

import jsonpatch
from oslo_config import cfg
import pecan
import wsme

from cloudpulse.common import exception
from cloudpulse.common.plugin import discover
from cloudpulse.common import utils
from cloudpulse import objects
from cloudpulse.openstack.common._i18n import _
from cloudpulse.scenario import base

CONF = cfg.CONF


JSONPATCH_EXCEPTIONS = (jsonpatch.JsonPatchException,
                        jsonpatch.JsonPointerException,
                        KeyError)


def validate_limit(limit):
    if limit is not None and limit <= 0:
        raise wsme.exc.ClientSideError(_("Limit must be positive"))

    return min(CONF.api.max_limit, limit) or CONF.api.max_limit


def validate_sort_dir(sort_dir):
    if sort_dir not in ['asc', 'desc']:
        raise wsme.exc.ClientSideError(_("Invalid sort direction: %s. "
                                         "Acceptable values are "
                                         "'asc' or 'desc'") % sort_dir)
    return sort_dir


def apply_jsonpatch(doc, patch):
    return jsonpatch.apply_patch(doc, jsonpatch.JsonPatch(patch))


def get_rpc_resource(resource, resource_ident):
    """Get the RPC resource from the uuid or logical name.

    :param resource: the resource type.
    :param resource_ident: the UUID or logical name of the resource.

    :returns: The RPC resource.
    :raises: InvalidUuidOrName if the name or uuid provided is not valid.
    """
    resource = getattr(objects, resource)

    if utils.is_uuid_like(resource_ident):
        return resource.get_by_uuid(pecan.request.context, resource_ident)

    if utils.allow_logical_names():
        return resource.get_by_name(pecan.request.context, resource_ident)

    raise exception.InvalidUuidOrName(name=resource_ident)


def get_rpc_resource_detail(resource, resource_ident):
    resource = getattr(objects, resource)
    test = resource.get_by_uuid(pecan.request.context, resource_ident)
    discover.import_modules_from_package("cloudpulse.scenario.plugins")
    for scenario_group in discover.itersubclasses(base.Scenario):
        for method in dir(scenario_group):
            if test['name'] == method:
                scenario = scenario_group()
                callback = getattr(scenario, 'verbose')
    return callback()
