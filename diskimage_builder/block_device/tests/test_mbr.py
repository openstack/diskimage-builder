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

import fixtures
import logging
import os
import subprocess

import diskimage_builder.block_device.tests.test_base as tb

from diskimage_builder.block_device.level0.localloop import image_create
from diskimage_builder.block_device.level1.mbr import MBR


logger = logging.getLogger(__name__)


class TestMBR(tb.TestBase):

    disk_size_10M = 10 * 1024 * 1024
    disk_size_1G = 1024 * 1024 * 1024

    def _get_path_for_partx(self):
        """Searches and sets the path for partx

        Because different distributions store the partx binary
        at different places, there is the need to look for it.
        """

        dirs = ["/bin", "/usr/bin", "/sbin", "/usr/sbin"]

        for d in dirs:
            if os.path.exists(os.path.join(d, "partx")):
                return os.path.join(d, "partx")
                return
        # If not found, try without path.
        return "partx"

    def setUp(self):
        super(TestMBR, self).setUp()

        self.tmp_dir = fixtures.TempDir()
        self.useFixture(self.tmp_dir)
        self.image_path = os.path.join(self.tmp_dir.path, "image.raw")
        image_create(self.image_path, TestMBR.disk_size_1G)
        logger.debug("Temp image is %s", self.image_path)

        self.partx_args = [self._get_path_for_partx(), "--raw",
                           "--output", "NR,START,END,TYPE,FLAGS,SCHEME",
                           "-g", "-b", "-", self.image_path]

    def _run_partx(self, image_path):
        logger.info("Running command: %s", self.partx_args)
        return subprocess.check_output(self.partx_args).decode("ascii")

    def test_one_ext_partition(self):
        """Creates one partition and check correctness with partx."""

        with MBR(self.image_path, TestMBR.disk_size_1G, 1024 * 1024) as mbr:
            mbr.add_partition(False, False, TestMBR.disk_size_10M, 0x83)
        output = self._run_partx(self.image_path)
        self.assertEqual(
            "1 2048 2097151 0xf 0x0 dos\n"
            "5 4096 24575 0x83 0x0 dos\n", output)

    def test_zero_partitions(self):
        """Creates no partition and check correctness with partx."""

        with MBR(self.image_path, TestMBR.disk_size_1G, 1024 * 1024):
            pass
        output = self._run_partx(self.image_path)
        self.assertEqual("", output)

    def test_many_ext_partitions(self):
        """Creates many partition and check correctness with partx."""

        with MBR(self.image_path, TestMBR.disk_size_1G, 1024 * 1024) as mbr:
            for nr in range(0, 64):
                mbr.add_partition(False, False, TestMBR.disk_size_10M, 0x83)

        output = self._run_partx(self.image_path)

        lines = output.split("\n")
        self.assertEqual(66, len(lines))

        self.assertEqual(
            "1 2048 2097151 0xf 0x0 dos", lines[0])

        start_block = 4096
        end_block = start_block + TestMBR.disk_size_10M / 512 - 1
        for nr in range(1, 65):
            fields = lines[nr].split(" ")
            self.assertEqual(6, len(fields))
            self.assertEqual(nr + 4, int(fields[0]))
            self.assertEqual(start_block, int(fields[1]))
            self.assertEqual(end_block, int(fields[2]))
            self.assertEqual("0x83", fields[3])
            self.assertEqual("0x0", fields[4])
            self.assertEqual("dos", fields[5])
            start_block += 22528
            end_block = start_block + TestMBR.disk_size_10M / 512 - 1

    def test_one_pri_partition(self):
        """Creates one primary partition and check correctness with partx."""

        with MBR(self.image_path, TestMBR.disk_size_1G, 1024 * 1024) as mbr:
            mbr.add_partition(True, False, TestMBR.disk_size_10M, 0x83)

        output = self._run_partx(self.image_path)
        self.assertEqual(
            "1 2048 22527 0x83 0x0 dos\n", output)

    def test_three_pri_partition(self):
        """Creates three primary partition and check correctness with partx."""

        with MBR(self.image_path, TestMBR.disk_size_1G, 1024 * 1024) as mbr:
            for _ in range(3):
                mbr.add_partition(True, False, TestMBR.disk_size_10M, 0x83)

        output = self._run_partx(self.image_path)
        self.assertEqual(
            "1 2048 22527 0x83 0x0 dos\n"
            "2 22528 43007 0x83 0x0 dos\n"
            "3 43008 63487 0x83 0x0 dos\n", output)

    def test_many_pri_and_ext_partition(self):
        """Creates many primary and extended partitions."""

        with MBR(self.image_path, TestMBR.disk_size_1G, 1024 * 1024) as mbr:
            # Create three primary partitions
            for _ in range(3):
                mbr.add_partition(True, False, TestMBR.disk_size_10M, 0x83)
            for _ in range(7):
                mbr.add_partition(False, False, TestMBR.disk_size_10M, 0x83)

        output = self._run_partx(self.image_path)
        self.assertEqual(
            "1 2048 22527 0x83 0x0 dos\n"     # Primary 1
            "2 22528 43007 0x83 0x0 dos\n"    # Primary 2
            "3 43008 63487 0x83 0x0 dos\n"    # Primary 3
            "4 63488 2097151 0xf 0x0 dos\n"   # Extended
            "5 65536 86015 0x83 0x0 dos\n"    # Extended Partition 1
            "6 88064 108543 0x83 0x0 dos\n"   # Extended Partition 2
            "7 110592 131071 0x83 0x0 dos\n"  # ...
            "8 133120 153599 0x83 0x0 dos\n"
            "9 155648 176127 0x83 0x0 dos\n"
            "10 178176 198655 0x83 0x0 dos\n"
            "11 200704 221183 0x83 0x0 dos\n", output)
