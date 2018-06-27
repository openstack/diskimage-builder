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
import mock
import os

import diskimage_builder.block_device.tests.test_config as tc

from diskimage_builder.block_device.blockdevice import BlockDeviceState
from diskimage_builder.block_device.config import config_tree_to_graph
from diskimage_builder.block_device.config import create_graph
from diskimage_builder.block_device.level0.localloop import image_create
from diskimage_builder.block_device.level1.partition import PartitionNode

logger = logging.getLogger(__name__)


class TestGPT(tc.TestGraphGeneration):

    @mock.patch('diskimage_builder.block_device.level1.partitioning.exec_sudo')
    def test_gpt_efi(self, mock_exec_sudo):
        # Test the command-sequence for a GPT/EFI partition setup
        tree = self.load_config_file('gpt_efi.yaml')
        config = config_tree_to_graph(tree)

        state = BlockDeviceState()

        graph, call_order = create_graph(config, self.fake_default_config,
                                         state)

        # Create a fake temp backing file (we check the size of it,
        # etc).
        # TODO(ianw): exec_sudo is generically mocked out, thus the
        # actual creation is mocked out ... but we could do this
        # without root and use parted to create the partitions on this
        # for slightly better testing.  An exercise for another day...
        self.tmp_dir = fixtures.TempDir()
        self.useFixture(self.tmp_dir)
        self.image_path = os.path.join(self.tmp_dir.path, "image.raw")
        # should be sparse...
        image_create(self.image_path, 1024 * 1024 * 1024)
        logger.debug("Temp image in %s", self.image_path)

        # Fake state for the loopback device
        state['blockdev'] = {}
        state['blockdev']['image0'] = {}
        state['blockdev']['image0']['image'] = self.image_path
        state['blockdev']['image0']['device'] = "/dev/loopX"

        for node in call_order:
            if isinstance(node, PartitionNode):
                node.create()

        # check the parted call looks right
        parted_cmd = ['sgdisk', self.image_path,
                      '-n', '1:0:+8M', '-t', '1:EF00', '-c', '1:ESP',
                      '-n', '2:0:+8M', '-t', '2:EF02', '-c', '2:BSP',
                      '-n', '3:0:+1006M', '-t', '3:8300', '-c', '3:Root Part']
        cmd_sequence = [
            mock.call(parted_cmd),
            mock.call(['sync']),
            mock.call(['kpartx', '-avs', '/dev/loopX'])
        ]
        self.assertEqual(mock_exec_sudo.call_count, len(cmd_sequence))
        mock_exec_sudo.assert_has_calls(cmd_sequence)

        # Check two new partitions appear in state correctly
        self.assertDictEqual(state['blockdev']['ESP'],
                             {'device': '/dev/mapper/loopXp1'})
        self.assertDictEqual(state['blockdev']['BSP'],
                             {'device': '/dev/mapper/loopXp2'})
        self.assertDictEqual(state['blockdev']['Root Part'],
                             {'device': '/dev/mapper/loopXp3'})
