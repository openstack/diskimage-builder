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

import functools
import logging
import mock

import diskimage_builder.block_device.tests.test_config as tc

from diskimage_builder.block_device.config import config_tree_to_graph
from diskimage_builder.block_device.config import create_graph
from diskimage_builder.block_device.level3.mount import cmp_mount_order
from diskimage_builder.block_device.level3.mount import MountPointNode
from diskimage_builder.block_device.tests.test_base import TestBase

logger = logging.getLogger(__name__)


class TestMountComparator(TestBase):

    def test_mount_comparator(self):
        # This tests cmp_mount_order to ensure it sorts in the
        # expected order.  The comparator takes a tuple of
        # (mount_point, node_name) but we can ignore the name
        partitions = [
            ('/var/log', 'fake_log'),
            ('/boot', 'fake_boot'),
            ('/', 'fake_name'),
            ('/var', 'fake_name')]
        partitions.sort(key=functools.cmp_to_key(cmp_mount_order))

        res = list(x[0] for x in partitions)

        # "/" must be first
        self.assertEqual(res[0], '/')

        # /var before /var/log
        var_pos = res.index('/var')
        var_log_pos = res.index('/var/log')
        self.assertGreater(var_log_pos, var_pos)


class TestMountOrder(tc.TestGraphGeneration):

    @mock.patch('diskimage_builder.block_device.level3.mount.exec_sudo')
    def test_mount_order(self, mock_exec_sudo):
        # This is probably in order after graph creation, so ensure it
        # remains stable
        config = self.load_config_file('multiple_partitions_graph.yaml')

        state = {}

        graph, call_order = create_graph(config, self.fake_default_config,
                                         state)

        # build up some fake state so that we don't have to mock out
        # all the parent calls that would really make these values, as
        # we just want to test MountPointNode
        state['filesys'] = {}
        state['filesys']['mkfs_root'] = {}
        state['filesys']['mkfs_root']['device'] = 'fake'
        state['filesys']['mkfs_var'] = {}
        state['filesys']['mkfs_var']['device'] = 'fake'
        state['filesys']['mkfs_var_log'] = {}
        state['filesys']['mkfs_var_log']['device'] = 'fake'

        for node in call_order:
            if isinstance(node, MountPointNode):
                # XXX: do we even need to create?  We could test the
                # sudo arguments from the mock in the below asserts
                # too
                node.create()

        # ensure that partitions are mounted in order root->var->var/log
        self.assertListEqual(state['mount_order'], ['/', '/var', '/var/log'])

    @mock.patch('diskimage_builder.block_device.level3.mount.exec_sudo')
    def test_mount_order_unsorted(self, mock_exec_sudo):
        # As above, but this is out of order and gets sorted
        # so that root is mounted first.
        config = self.load_config_file('lvm_tree_partition_ordering.yaml')
        parsed_graph = config_tree_to_graph(config)
        state = {}

        graph, call_order = create_graph(parsed_graph,
                                         self.fake_default_config,
                                         state)
        state['filesys'] = {}
        state['filesys']['mkfs_root'] = {}
        state['filesys']['mkfs_root']['device'] = 'fake'
        state['filesys']['mkfs_var'] = {}
        state['filesys']['mkfs_var']['device'] = 'fake'
        state['filesys']['mkfs_boot'] = {}
        state['filesys']['mkfs_boot']['device'] = 'fake'

        for node in call_order:
            if isinstance(node, MountPointNode):
                node.create()

        # ensure that partitions are mounted in order / -> /boot -> /var
        self.assertListEqual(state['mount_order'], ['/', '/boot', '/var'])
