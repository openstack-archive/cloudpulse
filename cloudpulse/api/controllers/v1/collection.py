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

import pecan
from wsme import types as wtypes

from cloudpulse.api.controllers import base
from cloudpulse.api.controllers import link


class Collection(base.APIBase):

    next = wtypes.text
    """A link to retrieve the next subset of the collection"""

    @property
    def collection(self):
        return getattr(self, self._type)

    def has_next(self, limit):
        """Return whether collection has more items."""
        return len(self.collection) and len(self.collection) == limit

    def get_next(self, limit, url=None, **kwargs):
        """Return a link to the next subset of the collection."""
        if not self.has_next(limit):
            return wtypes.Unset

        resource_url = url or self._type
        q_args = ''.join(['%s=%s&' % (key, kwargs[key]) for key in kwargs])
        next_args = ('?%(args)slimit=%(limit)d&marker=%(marker)s'
                     % {'args': q_args, 'limit': limit,
                        'marker': self.collection[-1].uuid})

        return link.Link.make_link('next', pecan.request.host_url,
                                   resource_url, next_args).href
