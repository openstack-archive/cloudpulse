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

from __future__ import print_function
import ansible.runner


class AnsibleRunner(object):

    def __init__(self,
                 host_list=None,
                 remote_user=None,
                 sudo=False):
        self.host_list = host_list
        self.sudo = sudo

    def validate_host_parameters(self, host_list, remote_user):
        if host_list is None:
            host_list = self.host_list

        if remote_user is None:
            remote_user = self.remote_user

        if host_list is None or remote_user is None:
            print("Host list [%s], remote user [%s] are required" %
                  (host_list, remote_user))
            return (None, None)

        return (host_list, remote_user)

    def validate_results(self, results, checks=None):
        results['status'] = 'PASS'
        failed_hosts = []

        if results['dark']:
            failed_hosts.append(results['dark'].keys())
            results['status'] = 'FAIL'

        for node in results['contacted'].keys():
            if 'failed' in results['contacted'][node]:
                if results['contacted'][node]['failed'] is True:
                    results['status'] = 'FAIL'

        for node in results['contacted'].keys():
            rc = results['contacted'][node].get('rc', None)
            if rc is not None and rc != 0:
                failed_hosts.append(node)
                results['status'] = 'FAIL'

        if checks is None:
            # print "No additional checks validated"
            return results, failed_hosts

        for check in checks:
            key = check.keys()[0]
            value = check.values()[0]
            for node in results['contacted'].keys():
                if key in results['contacted'][node].keys():
                    if results['contacted'][node][key] != value:
                        failed_hosts.append(node)
                        results['status'] = 'FAIL'

        return (results, failed_hosts)

    def ansible_perform_operation(self,
                                  host_list=None,
                                  remote_user=None,
                                  remote_pass=None,
                                  module=None,
                                  complex_args=None,
                                  module_args='',
                                  environment=None,
                                  check=False,
                                  forks=2):
        (host_list, remote_user) = \
            self.validate_host_parameters(host_list, remote_user)
        if (host_list, remote_user) is (None, None):
            return None

        if module is None:
            return None

        runner = ansible.runner.Runner(
            module_name=module,
            host_list=host_list,
            remote_user=remote_user,
            remote_pass=remote_pass,
            module_args=module_args,
            complex_args=complex_args,
            environment=environment,
            check=check,
            forks=forks)

        results = runner.run()

        results, failed_hosts = self.validate_results(results)
        if results['status'] != 'PASS':
            pass
        return results, failed_hosts
