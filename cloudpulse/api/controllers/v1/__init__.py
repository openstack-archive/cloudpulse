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

"""
Version 1 of the Cloudpulse API

NOTE: IN PROGRESS AND NOT FULLY IMPLEMENTED.
"""

import datetime

import pecan
from pecan import rest
from webob import exc
import wsme
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from cloudpulse.api.controllers import link
from cloudpulse.api.controllers.v1 import cpulse

BASE_VERSION = 1

MIN_VER_STR = '1.1'

# v1.1: Add API changelog here
MAX_VER_STR = '1.1'


MIN_VER = '1.1'
MAX_VER = '1.1'


class APIBase(wtypes.Base):

    created_at = wsme.wsattr(datetime.datetime, readonly=True)
    """The time in UTC at which the object is created"""

    updated_at = wsme.wsattr(datetime.datetime, readonly=True)
    """The time in UTC at which the object is updated"""

    def as_dict(self):
        """Render this object as a dict of its fields."""
        return dict((k, getattr(self, k))
                    for k in self.fields
                    if hasattr(self, k) and
                    getattr(self, k) != wsme.Unset)

    def unset_fields_except(self, except_list=None):
        """Unset fields so they don't appear in the message body.

        :param except_list: A list of fields that won't be touched.

        """
        if except_list is None:
            except_list = []

        for k in self.as_dict():
            if k not in except_list:
                setattr(self, k, wsme.Unset)


class V1(APIBase):
    """The representation of the version 1 of the API."""

    id = wtypes.text
    """The ID of the version, also acts as the release number"""

    cpulse = [link.Link]
    """Links to the cpulse resource"""

    extcpulse = [link.Link]
    """Links to the cpulse extension resource"""

    @staticmethod
    def convert():
        v1 = V1()
        v1.id = "v1"
        v1.links = [link.Link.make_link('self', pecan.request.host_url,
                                        'v1', '', bookmark=True),
                    link.Link.make_link('describedby',
                                        'http://docs.openstack.org',
                                        'developer/cloudpulse/dev',
                                        'api-spec-v1.html',
                                        bookmark=True, type='text/html')
                    ]
        v1.cpulse = [link.Link.make_link('self', pecan.request.host_url,
                                         'cpulse', ''),
                     link.Link.make_link('bookmark',
                                         pecan.request.host_url,
                                         'cpulse', '',
                                         bookmark=True)
                     ]
        v1.cpulse_ext = [link.Link.make_link('self', pecan.request.host_url,
                                             'cpulse_ext', ''),
                         link.Link.make_link('bookmark',
                                             pecan.request.host_url,
                                             'cpulse_ext', '',
                                             bookmark=True)
                         ]
        return v1


class Controller(rest.RestController):
    """Version 1 API controller root."""

    cpulse = cpulse.cpulseController()

    @wsme_pecan.wsexpose(V1)
    def get(self):
        # NOTE: The reason why convert() it's being called for every
        #       request is because we need to get the host url from
        #       the request object to make the links.
        return V1.convert()

    def _check_version(self, version, headers=None):
        if headers is None:
            headers = {}
        # ensure that major version in the URL matches the header
        if version.major != BASE_VERSION:
            raise exc.HTTPNotAcceptable(_(
                "Mutually exclusive versions requested. Version %(ver)s "
                "requested but not supported by this service."
                "The supported version range is: "
                "[%(min)s, %(max)s].") % {'ver': version,
                                          'min': MIN_VER_STR,
                                          'max': MAX_VER_STR},
                headers=headers)
        # ensure the minor version is within the supported range
        if version < MIN_VER or version > MAX_VER:
            raise exc.HTTPNotAcceptable(_(
                "Version %(ver)s was requested but the minor version is not "
                "supported by this service. The supported version range is: "
                "[%(min)s, %(max)s].") % {'ver': version, 'min': MIN_VER_STR,
                                          'max': MAX_VER_STR}, headers=headers)

__all__ = (Controller)
