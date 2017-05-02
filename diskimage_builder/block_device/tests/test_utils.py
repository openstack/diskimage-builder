# Copyright 2016 Andreas Florath (andreas@florath.net)
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import testtools

from diskimage_builder.block_device.utils import parse_abs_size_spec


class TestLoggingConfig(testtools.TestCase):

    def test_parse_size_spec(self):
        map(lambda tspec:
            self.assertEqual(parse_abs_size_spec(tspec[0]), tspec[1]),
            [["20TiB", 20 * 1024**4],
             ["1024KiB", 1024 * 1024],
             ["1.2TB", 1.2 * 1000**4],
             ["2.4T", 2.4 * 1000**4],
             ["512B", 512],
             ["364", 364]])
