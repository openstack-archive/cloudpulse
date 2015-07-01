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

from cloudpulse.db.sqlalchemy import api as dbapi
from cloudpulse import objects
from cloudpulse.openstack.common._i18n import _LI
from cloudpulse.openstack.common import log as logging
from cloudpulse.TestManager import TestManager
from oslo_config import cfg
import sys
import threading
from threading import Timer

LOG = logging.getLogger(__name__)
dblock = threading.RLock()

CONF = cfg.CONFCONF = cfg.CONF

test_manager = TestManager.TestManager()


def acquireLock():
    dblock.acquire()


def releaseLock():
    dblock.release()


class cpulseTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(self, *self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True


def test_run(**kwargs):
    LOG.debug(_LI('Running Openstack test%s') % kwargs['test']['name'])
    test_manager.run(**kwargs)


testthreads = []


def delete_old_entries():
    tasks = CONF.periodic_tests
    num_range = len([key for key in tasks.keys() if int(tasks[key]) > 0])
    conn = dbapi.get_backend()
    conn.delete_old_tests(num_range)


def timerfunc(*args, **kwargs):
    context = None
    acquireLock()
    tests = objects.Cpulse.list(context)
    releaseLock()
    delete_old_entries()
    for test in tests:
        LOG.debug(_LI('Dumping REPFUNCTION %s') % test['uuid'])
        if test['state'] == 'created' and test['testtype'] == 'manual':
            methodtocall = getattr(sys.modules[__name__], 'test_run')
            # methodtocall()
            testthr = threading.Thread(name=test['name'],
                                       target=methodtocall,
                                       kwargs={'test': test})
            testthreads.append(testthr)
            testthr.start()
            LOG.debug(_LI('REPFUNCTION, exec test %s') % test['name'])
