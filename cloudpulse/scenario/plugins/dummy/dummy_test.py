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

from cloudpulse.scenario import base
from oslo_config import cfg

TESTS_OPTS = [
    cfg.IntOpt('dummy_cloudtest',
               default=0,
               help='The nova endpoint and interval')
]

CONF = cfg.CONF

periodic_test_group = cfg.OptGroup(name='periodic_tests',
                                   title='Periodic tests to be run')
CONF.register_opts(TESTS_OPTS, periodic_test_group)


class dummy_scenario(base.Scenario):
    @base.scenario(operator=True)
    def dummy_cloudtest(self, *args, **kwargs):
        return (200, "success", ['dummy_result'])

    def verbose(self, *args, **kwargs):
        # This is a sample entry which spcifies how the verbose call
        # should handle in each module.
        return [{'result': 'success',
                 'description': 'The test run successfully'}]
