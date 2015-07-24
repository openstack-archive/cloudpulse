# Copyright 2010-2011 OpenStack Foundation
# Copyright (c) 2013 Cisco Inc
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

from cloudpulse.db import api as db_api


def get_cpulse_test(**kw):
    return {
        'id': kw.get('id', 32),
        'uuid': kw.get('uuid', 'e74c40e0-d825-11e2-a28f-0800200c9a66'),
        'name': kw.get('name', 'dummy_cloudtest'),
        'state': kw.get('state', 'created'),
        'result': kw.get('state', 'success'),
        'testtype': kw.get('testtype', 'periodic'),
        'created_at': kw.get('created_at'),
        'updated_at': kw.get('updated_at'),
    }


def create_cpulse_test(**kw):
    test = get_cpulse_test(**kw)
    dbapi = db_api.get_instance()
    return dbapi.create_test(test)
