# Copyright 2013 UnitedStack Inc.
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

import datetime

import pecan
from pecan import rest
import wsme
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from cloudpulse.api.controllers import base
from cloudpulse.api.controllers import link
from cloudpulse.api.controllers.v1 import collection
from cloudpulse.api.controllers.v1 import types
from cloudpulse.api.controllers.v1 import utils as api_utils
from cloudpulse import objects


class CpulsePatchType(types.JsonPatchType):

    @staticmethod
    def mandatory_attrs():
        return ['/uuid']


class Cpulse(base.APIBase):
    """API representation of a test.

    This class enforces type checking and value constraints, and converts
    between the internal object model and the API representation of a test.
    """
    id = wtypes.IntegerType(minimum=1)

    uuid = types.uuid
    """Unique UUID for this test"""

    name = wtypes.StringType(min_length=1, max_length=255)
    """Name of this test"""

    state = wtypes.StringType(min_length=1, max_length=255)
    """State of this test"""

    cpulse_create_timeout = wtypes.IntegerType(minimum=0)
    """Timeout for creating the test in minutes. Set to 0 for no timeout."""
    links = wsme.wsattr([link.Link], readonly=True)
    """A list containing a self link and associated test links"""

    result = wtypes.StringType(min_length=1, max_length=1024)
    """Result of this test"""

    testtype = wtypes.StringType(min_length=1, max_length=255)

    def __init__(self, **kwargs):
        super(Cpulse, self).__init__()

        self.fields = []
        for field in objects.Cpulse.fields:
            # Skip fields we do not expose.
            if not hasattr(self, field):
                continue
            self.fields.append(field)
            setattr(self, field, kwargs.get(field, wtypes.Unset))

    @staticmethod
    def _convert_with_links(cpulse, url, expand=True):
        if not expand:
            cpulse.unset_fields_except(['uuid', 'name', 'state', 'id',
                                        'result', 'testtype'])
        return cpulse

    @classmethod
    def convert_with_links(cls, rpc_test, expand=True):
        test = Cpulse(**rpc_test.as_dict())
        return cls._convert_with_links(test, pecan.request.host_url, expand)

    @classmethod
    def sample(cls, expand=True):
        sample = cls(uuid='27e3153e-d5bf-4b7e-b517-fb518e17f34c',
                     name='example',
                     state="CREATED",
                     result="NotYetRun",
                     created_at=datetime.datetime.utcnow(),
                     updated_at=datetime.datetime.utcnow())
        return cls._convert_with_links(sample, 'http://localhost:9511', expand)


class CpulseCollection(collection.Collection):
    """API representation of a collection of tests."""

    cpulses = [Cpulse]
    """A list containing tests objects"""

    def __init__(self, **kwargs):
        self._type = 'cpulses'

    @staticmethod
    def convert_with_links(rpc_tests, limit, url=None, expand=False, **kwargs):
        collection = CpulseCollection()
        collection.cpulses = [Cpulse.convert_with_links(p, expand)
                              for p in rpc_tests]
        collection.next = collection.get_next(limit, url=url, **kwargs)
        return collection

    @classmethod
    def sample(cls):
        sample = cls()
        sample.cpulse = [Cpulse.sample(expand=False)]
        return sample


class cpulseController(rest.RestController):
    """REST controller for Cpulse.."""
    def __init__(self):
        super(cpulseController, self).__init__()

    _custom_actions = {'detail': ['GET']}

    def _get_tests_collection(self, marker, limit,
                              sort_key, sort_dir, expand=False,
                              resource_url=None):

        limit = api_utils.validate_limit(limit)
        sort_dir = api_utils.validate_sort_dir(sort_dir)

        marker_obj = None
        if marker:
            marker_obj = objects.Cpulse.get_by_uuid(pecan.request.context,
                                                    marker)

        tests = pecan.request.rpcapi.test_list(pecan.request.context, limit,
                                               marker_obj, sort_key=sort_key,
                                               sort_dir=sort_dir)

        return CpulseCollection.convert_with_links(tests, limit,
                                                   url=resource_url,
                                                   expand=expand,
                                                   sort_key=sort_key,
                                                   sort_dir=sort_dir)

    @wsme_pecan.wsexpose(CpulseCollection, types.uuid,
                         types.uuid, int, wtypes.text, wtypes.text)
    def get_all(self, test_uuid=None, marker=None, limit=None,
                sort_key='id', sort_dir='asc'):
        """Retrieve a list of tests.

        :param marker: pagination marker for large data sets.
        :param limit: maximum number of resources to return in a single result.
        :param sort_key: column to sort results by. Default: id.
        :param sort_dir: direction to sort. "asc" or "desc". Default: asc.
        """
        return self._get_tests_collection(marker, limit, sort_key,
                                          sort_dir)

    @wsme_pecan.wsexpose(Cpulse, types.uuid_or_name)
    def get_one(self, test_ident):
        """Retrieve information about the given test.

        :param test_ident: UUID of a test or logical name of the test.
        """

        rpc_test = api_utils.get_rpc_resource('Cpulse', test_ident)

        return Cpulse.convert_with_links(rpc_test)

    @pecan.expose('json')
    def detail(self, test_ident):
        """Retrieve detail information about the given test.

        :param test_ident: UUID of a test or logical name of the test.
        """
        rpc_test_detail = api_utils.get_rpc_resource_detail('Cpulse',
                                                            test_ident)
        return rpc_test_detail

    @wsme_pecan.wsexpose(Cpulse, body=Cpulse, status_code=201)
    def post(self, test):
        """Create a new test.

        :param test: a test within the request body.
        """

        test_dict = test.as_dict()
        context = pecan.request.context
        auth_token = context.auth_token_info['token']
        test_dict['project_id'] = auth_token['project']['id']
        test_dict['user_id'] = auth_token['user']['id']
        ncp = objects.Cpulse(context, **test_dict)
        ncp.cpulse_create_timeout = 0
        ncp.result = "NotYetRun"
        ncp.testtype = "manual"
        ncp.state = 'created'
        res_test = pecan.request.rpcapi.test_create(ncp,
                                                    ncp.cpulse_create_timeout)

        return Cpulse.convert_with_links(res_test)

    @wsme_pecan.wsexpose(None, types.uuid_or_name, status_code=204)
    def delete(self, test_ident):
        """Delete a test.

        :param test_ident: UUID of a test or logical name of the test.
        """

        context = pecan.request.context

        rpc_test = api_utils.get_rpc_resource('Cpulse', test_ident)

        pecan.request.rpcapi.test_delete(context, rpc_test.uuid)
