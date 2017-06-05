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

import logging

import diskimage_builder.block_device.tests.test_base as tb

from diskimage_builder.block_device.utils import parse_abs_size_spec
from diskimage_builder.block_device.utils import parse_rel_size_spec


logger = logging.getLogger(__name__)


class TestBlockDeviceUtils(tb.TestBase):
    """Tests for the utils.py

    This tests mostly the error and failure cases - because the good
    cases are tested implicitly with the higher level unit tests.
    """

    def test_parse_rel_size_with_abs(self):
        """Calls parse_rel_size_spec with an absolute number"""

        is_rel, size = parse_rel_size_spec("154MiB", 0)
        self.assertFalse(is_rel)
        self.assertEqual(154 * 1024 * 1024, size)

    def test_parse_abs_size_without_spec(self):
        """Call parse_abs_size_spec without spec"""

        size = parse_abs_size_spec("198")
        self.assertEqual(198, size)

    def test_invalid_unit_spec(self):
        """Call parse_abs_size_spec with invalid unit spec"""

        self.assertRaises(RuntimeError, parse_abs_size_spec, "747InVaLiDUnIt")

    def test_broken_unit_spec(self):
        """Call parse_abs_size_spec with a completely broken unit spec"""

        self.assertRaises(RuntimeError, parse_abs_size_spec, "_+!HuHi+-=")

    def test_parse_size_spec(self):
        map(lambda tspec:
            self.assertEqual(parse_abs_size_spec(tspec[0]), tspec[1]),
            [["20TiB", 20 * 1024**4],
             ["1024KiB", 1024 * 1024],
             ["1.2TB", 1.2 * 1000**4],
             ["2.4T", 2.4 * 1000**4],
             ["512B", 512],
             ["364", 364]])
