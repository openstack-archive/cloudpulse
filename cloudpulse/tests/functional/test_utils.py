# Copyright 2010-2011 OpenStack Foundation
# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
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

import os
import re
import yaml


def form_cmd(cmd):
    command = 'cloudpulse %s ' % (cmd)
    return command


def parse_run_cmd_result(result):
    """Just checking whether a test is created or not"""
    status = 'Fail'
    if result:
        if 'state' in result and 'created' in result:
            status = 'Pass'
    return status


def parse_result_cmd_result(result):
    status = 'Fail'
    if result:
        if 'uuid' in result and 'id' in result and 'testtype' in result:
            status = 'Pass'
    return status


def parse_show_cmd_result(result, uuid):
    status = 'Fail'
    if result:
        if uuid in result and 'state' in result:
            status = 'Pass'
    return status


def parse_endpoint_result(result, uuid):
    status = 'Pass'
    if result:
        if uuid in result and 'failed' in result:
            status = 'Fail'
    return status


def get_uuid(result):
    uuid = ''
    left, right_str = result.split('uuid')
    pattern = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    res = re.search(pattern, result)
    if res:
        uuid = res.group()
    return uuid


def get_environ_variables():
    env_var = {}
    env = os.environ
    env_var.update({'OS_USERNAME': env.get('OS_USERNAME')})
    env_var.update({'OS_PASSWORD': env.get('OS_PASSWORD')})
    env_var.update({'OS_TENANT_NAME': env.get('OS_TENANT_NAME')})
    env_var.update({'OS_AUTH_URL': env.get('OS_AUTH_URL')})
    env_var.update(
        {'OS_IDENTITY_API_VERSION': env.get('OS_IDENTITY_API_VERSION')})
    env_var.update(
        {'OS_VOLUME_API_VERSION': env.get('OS_VOLUME_API_VERSION')})
    return env_var


def form_cli_env_params(env, invalid_uname=False, invalid_pwd=False,
                        invalid_tenant=False, invalid_auth=False):
    opt = ''
    if not invalid_uname:
        opt += '--os-username ' + env['OS_USERNAME']
    else:
        opt += '--os-username ' + env['OS_USERNAME'] + '1'
    if not invalid_pwd:
        opt += ' --os-password ' + env['OS_PASSWORD']
    else:
        opt += ' --os-password ' + env['OS_PASSWORD'] + '1'
    if not invalid_tenant:
        opt += ' --os-tenant-name ' + env['OS_TENANT_NAME']
    else:
        opt += ' --os-tenant-name ' + env['OS_TENANT_NAME'] + '1'
    if not invalid_auth:
        opt += ' --os-auth-url ' + env['OS_AUTH_URL']
    else:
        opt += ' --os-auth-url ' + env['OS_AUTH_URL'] + '1'
    return opt


def get_last_test_id(list_data):
    last_testcase_id = 0
    needed_data = list_data[3:-1]
    last_testcase_id = int(needed_data[-1].split('|')[2])
    return last_testcase_id


def parse_test_case_result(data):
    result = data[3:-1]
    results = []
    for item in result:
        x, uuid, idd, name, testtype, state, no = item.split('|')
        d = {}
        d.update({'uuid': uuid})
        d.update({'id': int(idd)})
        d.update({'name': name})
        d.update({'testtype': testtype})
        d.update({'state': state})
        results.append(d)
    return results


def form_start_service_cmd(service_name=None):
    cmd = None
    if service_name:
        cmd = 'systemctl start %s' % service_name
    return cmd


def form_stop_service_cmd(service_name=None):
    cmd = None
    if service_name:
        cmd = 'systemctl stop %s' % service_name
    return cmd


def get_absolute_path_for_file(path, file_name, splitdir=None):
    """Return filename in absolute path for any file passed as relative path"""
    base = os.path.basename(path)
    if splitdir is not None:
        splitdir = splitdir + "/" + base
    else:
        splitdir = base
    if os.path.isabs(path):
        abs_file_path = os.path.join(path.split(splitdir)[0],
                                     file_name)
    else:
        abs_file = os.path.abspath(path)
        abs_file_path = os.path.join(abs_file.split(splitdir)[0],
                                     file_name)
    return abs_file_path


def create_parsed_yaml(yaml_file):
    """Create a parsed yaml dictionalry from the yaml file."""
    try:
        fp = open(yaml_file)
    except IOError as ioerr:
        print ("Failed to open file %s [%s]" % (yaml_file, ioerr))
        raise IOError(ioerr)
    try:
        parsed = yaml.safe_load(fp)
    except yaml.error.YAMLError as perr:
        print ("Failed to parse %s [%s]" % (yaml_file, perr))
        return None
    fp.close()
    return parsed
