# Copyright 2014 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import tempfile
import time

from diskimage_builder.tests import base


class TestCacheUrl(base.ScriptTestBase):
    def test_cache_url_caches(self):
        tempdir = tempfile.mkdtemp()
        target = os.path.join(tempdir, 'target')
        source = 'http://fake/url'
        # Write fake data to the target file and return success
        self._stub_script('curl', 'echo "test" > ${3:7:100}\necho 200')
        self._run_command(
            ['diskimage_builder/elements/cache-url/bin/cache-url',
             source, target])
        self.assertTrue(os.path.exists(target))
        modification_time = os.path.getmtime(target)
        # Make sure that the timestamp would change if the file does
        time.sleep(1)
        self._stub_script('curl', 'echo "304"')
        self._run_command(
            ['diskimage_builder/elements/cache-url/bin/cache-url',
             source, target])
        self.assertEqual(modification_time, os.path.getmtime(target))
