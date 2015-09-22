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

from cloudpulse.common import context as cloudpulse_context
from cloudpulse.common.plugin import discover
from cloudpulse.common import utils
from cloudpulse.conductor import cpulse_lock
from cloudpulse.db.sqlalchemy import api as dbapi
from cloudpulse import objects
from cloudpulse.openstack.common import service as os_service
from cloudpulse.scenario import base
import datetime
import logging
from oslo_config import cfg
from oslo_utils import importutils
import pytz
import textwrap

cfg.CONF.import_opt('auth_uri', 'keystonemiddleware.auth_token',
                    group='keystone_authtoken')


CONF = cfg.CONF

LOG = logging.getLogger(__name__)


class Periodic_Task(object):

    def __init__(self, task):
        self.task = task
        self.conductor_id = '1'

    def create_task_entry(self, context):
        test = {}
        test['state'] = 'created'
        test['testtype'] = 'periodic'
        test['name'] = self.task
        test['uuid'] = utils.generate_uuid()
        new_test = objects.Cpulse(context, **test)
        with cpulse_lock.thread_lock(new_test, self.conductor_id):
            new_test.create()
        return new_test

    def check_if_already_run(self, context):
        tasks = CONF.periodic_tests
        task_interval = int(tasks[self.task])
        filters = {}
        filters['name'] = self.task
        tests = objects.Cpulse.list(context, filters=filters)
        if tests:
            lasttest = objects.Cpulse.list(context, filters=filters)[-1]
            lastime = lasttest['created_at']
            timenow = datetime.datetime.now(pytz.utc)
            timesincelast = (timenow - lastime).seconds
            if timesincelast >= task_interval:
                return True
            else:
                return False
        else:
            return True

    def run_task(self):
        importutils.import_module('keystonemiddleware.auth_token')
        username = cfg.CONF.keystone_authtoken.username
        tenant_name = cfg.CONF.keystone_authtoken.project_name
        # password = cfg.CONF.keystone_authtoken.password
        auth_url = cfg.CONF.keystone_authtoken.auth_uri

        context = cloudpulse_context.make_context(
            auth_url=auth_url,
            user=username,
            project=tenant_name)
        if self.check_if_already_run(context):
            new_test = self.create_task_entry(context)
            test_manager.run(test=new_test)


class Periodic_TestManager(os_service.Service):

    def __init__(self):
        super(Periodic_TestManager, self).__init__()

    def start(self):
        tasks = CONF.periodic_tests
        for key in tasks.keys():
            interval, task_name = tasks[key], key
            if int(interval) > 0:
                period_task = Periodic_Task(task_name)
                self.tg.add_timer(interval, self.interval_task,
                                  task=period_task)

    @staticmethod
    def interval_task(task):
        task.run_task()


class TestManager(object):

    def __init__(self):
        self.command_ref = {}
        self.conductor_id = '1'
        discover.import_modules_from_package("cloudpulse.scenario.plugins")
        for scenario_group in discover.itersubclasses(base.Scenario):
            for method in dir(scenario_group):
                scenario = scenario_group()
                callback = getattr(scenario, method)
                self.command_ref[method] = callback

    def run(self, **kwargs):
        Test = kwargs['test']
        func = self.command_ref[Test['name']]
        Test['state'] = 'running'
        with cpulse_lock.thread_lock(Test, self.conductor_id):
            self.update_test(Test['uuid'], Test)
        result = func()
        if result[0] == 200:
            Test['state'] = 'success'
            Test['result'] = textwrap.fill(str(result[1]), 40)
        else:
            Test['state'] = 'failed'
            Test['result'] = textwrap.fill(str(result[1]), 40)
        with cpulse_lock.thread_lock(Test, self.conductor_id):
            self.update_test(Test['uuid'], Test)

    def run_periodic(self, **kwargs):
        Test = kwargs['test']
        func = self.command_ref[Test['name']]
        result = func()
        if result[0] == 200:
            Test['result'] = textwrap.fill(str(result[1]), 40)
        else:
            Test['state'] = 'failed'
            Test['result'] = textwrap.fill(str(result[1]), 40)
        with cpulse_lock.thread_lock(Test, self.conductor_id):
            self.update_test(Test['uuid'], Test)

    def update_test(self, tuuid, patch):
        npatch = {}
        npatch['state'] = patch['state']
        npatch['id'] = patch['id']
        npatch['name'] = patch['name']
        npatch['result'] = patch['result']
        conn = dbapi.get_backend()
        conn.update_test(tuuid, npatch)
        return npatch

test_manager = TestManager()
