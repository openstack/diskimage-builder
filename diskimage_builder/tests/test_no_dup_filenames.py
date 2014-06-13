# Copyright 2014 Red Hat, Inc.
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

import glob
import os


import testtools


class TestNoDupFilenames(testtools.TestCase):

    def test_no_dup_filenames(self):
        topdir = os.path.normpath(os.path.dirname(__file__) + '/../../')
        elements_glob = os.path.join(topdir, "elements", "*")

        filenames = []
        dirs_to_check = ['block-device.d', 'cleanup.d', 'extra-data.d',
                         'finalise.d', 'install.d', 'post-install.d',
                         'pre-install.d', 'root.d']

        for element_dir in glob.iglob(elements_glob):
            for dir_to_check in dirs_to_check:
                target_dir = os.path.join(element_dir, dir_to_check, "*")
                for target in glob.iglob(target_dir):
                    short_path = target[len(element_dir) + 1:]
                    if not os.path.isdir(target):
                        err_msg = 'Duplicate file name found %s' % short_path
                        self.assertFalse(short_path in filenames, err_msg)
                        filenames.append(short_path)
