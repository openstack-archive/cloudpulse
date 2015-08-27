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

from cloudpulse.common import exception
from cloudpulse import objects
import contextlib
import logging
from oslo_utils import excutils

LOG = logging.getLogger(__name__)


class CpulseLock(object):

    def __init__(self, cpulse_test, conductor_id):
        self.cpulse_test = cpulse_test
        self.conductor_id = conductor_id

    def acquire(self, retry=True):
        lock_conductor_id = objects.CpulseLock.create(self.cpulse_test.name,
                                                      self.conductor_id)
        if lock_conductor_id is None:
            return
        else:
            raise exception.TestLocked(uuid=self.cpulse_test.name)

    def release(self, test_name):
        result = objects.CpulseLock.release(test_name, self.conductor_id)
        if result is True:
            LOG.debug("Lock was already released on test %s!" % test_name)
        else:
            LOG.debug("Lock has been released")


@contextlib.contextmanager
def thread_lock(cpulse_test, conductor_id):
    cpulselock = CpulseLock(cpulse_test, conductor_id)
    try:
        cpulselock.acquire()
        yield
    except exception.TestLocked:
        raise
    except:  # noqa
        with excutils.save_and_reraise_exception():
            cpulselock.release(cpulse_test.name)
    finally:
        cpulselock.release(cpulse_test.name)
