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

from cloudpulse.common.plugin import discover
from cloudpulse.scenario import base
from oslo_config import cfg

cfg.CONF.import_opt('auth_uri', 'keystonemiddleware.auth_token',
                    group='keystone_authtoken')

TESTS_OPTS = [
    cfg.IntOpt('all_tests',
               default=0,
               help='Run all tests')
]

CONF = cfg.CONF

periodic_test_group = cfg.OptGroup(name='periodic_tests',
                                   title='Periodic tests to be run')
CONF.register_group(periodic_test_group)
CONF.register_opts(TESTS_OPTS, periodic_test_group)


class all_scenario(base.Scenario):

    @base.scenario(admin_only=False, operator=False)
    def all_tests(self):
        enabled_scenarios = cfg.CONF.scenario.enabled_scenarios
        all_cases = []
        result = 200
        resultmsg = ''
        discover.import_modules_from_package("cloudpulse.scenario.plugins")
        for scenario_group in discover.itersubclasses(base.Scenario):
            if scenario_group.__name__ in enabled_scenarios:
                all_cases += [getattr(scenario_group(), method)
                              for method in dir(scenario_group)
                              if method.startswith("all")]
        for func in all_cases:
            try:
                funres = func()
            except Exception as e:
                funres = [404, str(e)]
            if funres[0] != 200:
                resultmsg += ("%s\n\n" % (funres[1]))
                result = 404
        if not resultmsg:
            resultmsg = "All Tests passed"
        return (result, resultmsg)
