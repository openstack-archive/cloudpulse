from cloudpulse.db.sqlalchemy import api as dbapi
from cloudpulse.objects.cpulse import Cpulse
from cloudpulse import objects
from cloudpulse.openstack.common._i18n import _LI
from cloudpulse.openstack.common import log as logging
from cloudpulse.api.controllers.v1 import utils as api_utils
from cloudpulse.common import clients
from cloudpulse.common import context as thread_context
from oslo_config import cfg
from cloudpulse.TestManager import TestManager
import sys
from threading import Timer
from time import sleep
import threading
import pecan

LOG = logging.getLogger(__name__)
dblock = threading.RLock()

test_manager = TestManager.TestManager()

def acquireLock():
    dblock.acquire()

def releaseLock():
    dblock.release()

class cpulseTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
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
    LOG.info(_LI('Running Openstack test%s') % kwargs['test']['name'])
    test_manager.run(**kwargs)



testthreads=[]
def timerfunc(*args, **kwargs):
    context=None
    acquireLock()
    tests = objects.Cpulse.list(context)
    releaseLock()
    for test in tests:
        LOG.info(_LI('Dumping REPFUNCTION %s') % test['uuid'])
        if test['state'] == 'created' and test['testtype'] == 'manual':
            methodtocall = getattr(sys.modules[__name__], 'test_run')
	    # methodtocall()
	    testthr = threading.Thread(name=test['name'], target=methodtocall, kwargs={'test' : test })
            testthreads.append(testthr)
            testthr.start()
            LOG.info(_LI('REPFUNCTION, exec test %s') % test['name'])
