# Copyright 2013 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""
Base classes for storage engines
"""

import abc

from oslo_config import cfg
from oslo_db import api as db_api
import six


_BACKEND_MAPPING = {'sqlalchemy': 'cloudpulse.db.sqlalchemy.api'}
IMPL = db_api.DBAPI.from_config(cfg.CONF, backend_mapping=_BACKEND_MAPPING,
                                lazy=True)


def get_instance():
    """Return a DB API instance."""
    return IMPL


@six.add_metaclass(abc.ABCMeta)
class Connection(object):
    """Base class for storage system connections."""

    @abc.abstractmethod
    def __init__(self):
        """Constructor."""

    @abc.abstractmethod
    def get_test_list(self, context, columns=None, filters=None, limit=None,
                      marker=None, sort_key=None, sort_dir=None):
        """Get specific columns for matching tests.

        Return a list of the specified columns for all tess that match the
        specified filters.

        :param context: The security context
        :param columns: List of column names to return.
                        Defaults to 'id' column when columns == None.
        :param filters: Filters to apply. Defaults to None.

        :param limit: Maximum number of tests to return.
        :param marker: the last item of the previous page; we return the next
                       result set.
        :param sort_key: Attribute by which results should be sorted.
        :param sort_dir: direction in which results should be sorted.
                         (asc, desc)
        :returns: A list of tuples of the specified columns.
        """

    @abc.abstractmethod
    def create_test(self, values):
        """Create a new test.

        :param values: A dict containing several items used to identify
                       and track the test, and several dicts which are passed
                       into the Drivers when managing this test. For example:

                       ::

                        {
                         'uuid': utils.generate_uuid(),
                         'name': 'endpoint_functional',
                         'state': 'created',
                         'result': 'pass'
                        }
        :returns: A test.
        """

    @abc.abstractmethod
    def get_test_by_id(self, context, test_id):
        """Return a test.

        :param context: The security context
        :param test_id: The id of a test.
        :returns: A test.
        """

    @abc.abstractmethod
    def get_test_by_uuid(self, context, test_uuid):
        """Return a test.

        :param context: The security context
        :param test_uuid: The uuid of a test.
        :returns: A test.
        """

    @abc.abstractmethod
    def get_test_by_name(self, context, test_name):
        """Return a test.

        :param context: The security context
        :param test_name: The name of a test.
        :returns: A test.
        """

    @abc.abstractmethod
    def destroy_test(self, test_id):
        """Destroy a test.and all associated interfaces.

        :param test_id: The id or uuid of a test.
        """

    @abc.abstractmethod
    def update_test(self, test_id, values):
        """Update properties of a test.

        :param test_id: The id or uuid of a test.
        :returns: A test.
        :raises: TestNotFound
        """

    @abc.abstractmethod
    def create_test_lock(self, test_name):
        """Create a new testlock.

        This method will fail if the test has already been locked.

        :param test_name: The name of a test.
        :returns: None if success.
                  Otherwise, the id of the the test.
        """

    @abc.abstractmethod
    def steal_test_lock(self, test_name):
        """Steal lock of a test.

        Lock the test with test id if the test is currently locked.

        :param test_name: The name of a test.
        :returns: None if success. True if the test is not locked.
                  Otherwise, the id of the test.
        """

    @abc.abstractmethod
    def release_test_lock(self, test_name):
        """Release lock of a test.

        :param test_name: The name of a test.
        :returns: None if success. True otherwise.
        """
