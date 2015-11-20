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
import pwd
import remote_filecredentials as filecredentials
import stat


class FileTraversal(object):

    def file_traversal(self, dir_list, file_dir):
        try:

            output = {}
            for dir_name in dir_list:
                self.rootDir = dir_name
                for dirName, subdirList, fileList in os.walk(self.rootDir):
                    os.chdir(dirName)
                    for f1 in fileList:
                        st = os.stat(f1)
                        ins = filecredentials.AccessPreveliges(
                            f1, st[stat.ST_SIZE], oct(
                                stat.S_IMODE(
                                    st[
                                        stat.ST_MODE])), pwd.getpwuid(
                                st[stat.ST_UID]), pwd.getpwuid(
                                st[stat.ST_GID]))
                        output.update(
                            {
                                ins.getName(): {
                                    'size': ins.getSize(),
                                    'mode': ins.getMode(),
                                    'user': ins.getUser(),
                                    'group': ins.getGroup()}})
            print (output)
        except Exception as e:
            print (e)


if __name__ == '__main__':
    # LOG.info('Executing test')
    file_dir = '/var/sec_hc/'
    dirs = []
    with open(file_dir + 'dir_list') as f:
        dirs = f.read().splitlines()

    sec = FileTraversal()

    # LOG.info('Executing test1')
    sec.file_traversal(dirs, file_dir)
