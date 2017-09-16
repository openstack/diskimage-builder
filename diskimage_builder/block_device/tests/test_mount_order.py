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
import os

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

    def _exec_sudo_log(*args, **kwargs):
        # Used as a side-effect from exec_sudo mocking so we can see
        # the call in-place in logs
        logger.debug("exec_sudo: %s", " ".join(args[0]))

    @mock.patch('diskimage_builder.block_device.level3.mount.exec_sudo',
                side_effect=_exec_sudo_log)
    def test_mount_order(self, mock_exec_sudo):
        # XXX: better mocking for the os.path.exists calls to avoid
        # failing if this exists.
        self.assertFalse(os.path.exists('/fake/'))

        # This is probably in order after graph creation, so ensure it
        # remains stable.  We test the mount and umount call sequences
        config = self.load_config_file('multiple_partitions_graph.yaml')
        state = {}
        graph, call_order = create_graph(config, self.fake_default_config,
                                         state)

        # build up some fake state so that we don't have to mock out
        # all the parent calls that would really make these values, as
        # we just want to test MountPointNode
        state['filesys'] = {
            'mkfs_root': {'device': 'fake_root_device'},
            'mkfs_var': {'device': 'fake_var_device'},
            'mkfs_var_log': {'device': 'fake_var_log_device'}
        }

        for node in call_order:
            if isinstance(node, MountPointNode):
                node.create()
        for node in reversed(call_order):
            if isinstance(node, MountPointNode):
                node.umount()

        # ensure that partitions are mounted in order root->var->var/log
        self.assertListEqual(state['mount_order'], ['/', '/var', '/var/log'])

        cmd_sequence = [
            # mount sequence
            mock.call(['mkdir', '-p', '/fake/']),
            mock.call(['mount', 'fake_root_device', '/fake/']),
            mock.call(['mkdir', '-p', '/fake/var']),
            mock.call(['mount', 'fake_var_device', '/fake/var']),
            mock.call(['mkdir', '-p', '/fake/var/log']),
            mock.call(['mount', 'fake_var_log_device', '/fake/var/log']),
            # umount sequence
            mock.call(['sync']),
            mock.call(['fstrim', '--verbose', '/fake/var/log']),
            mock.call(['umount', '/fake/var/log']),
            mock.call(['sync']),
            mock.call(['fstrim', '--verbose', '/fake/var']),
            mock.call(['umount', '/fake/var']),
            mock.call(['sync']),
            mock.call(['fstrim', '--verbose', '/fake/']),
            mock.call(['umount', '/fake/'])
        ]
        self.assertListEqual(mock_exec_sudo.call_args_list, cmd_sequence)

    @mock.patch('diskimage_builder.block_device.level3.mount.exec_sudo',
                side_effect=_exec_sudo_log)
    def test_mount_order_unsorted(self, mock_exec_sudo):
        # As above, but this is out of order and gets sorted
        # so that root is mounted first.
        config = self.load_config_file('lvm_tree_partition_ordering.yaml')
        parsed_graph = config_tree_to_graph(config)
        state = {}

        graph, call_order = create_graph(parsed_graph,
                                         self.fake_default_config,
                                         state)
        state['filesys'] = {
            'mkfs_root': {'device': 'fake_root_device'},
            'mkfs_var': {'device': 'fake_var_device'},
            'mkfs_boot': {'device': 'fake_boot_device'}
        }

        for node in call_order:
            if isinstance(node, MountPointNode):
                node.create()
        for node in reversed(call_order):
            if isinstance(node, MountPointNode):
                node.umount()

        # ensure that partitions are mounted in order / -> /boot -> /var
        self.assertListEqual(state['mount_order'], ['/', '/boot', '/var'])

        cmd_sequence = [
            # mount sequence
            mock.call(['mkdir', '-p', '/fake/']),
            mock.call(['mount', 'fake_root_device', '/fake/']),
            mock.call(['mkdir', '-p', '/fake/boot']),
            mock.call(['mount', 'fake_boot_device', '/fake/boot']),
            mock.call(['mkdir', '-p', '/fake/var']),
            mock.call(['mount', 'fake_var_device', '/fake/var']),
            # umount sequence
            mock.call(['sync']),
            mock.call(['fstrim', '--verbose', '/fake/var']),
            mock.call(['umount', '/fake/var']),
            mock.call(['sync']),
            mock.call(['fstrim', '--verbose', '/fake/boot']),
            mock.call(['umount', '/fake/boot']),
            mock.call(['sync']),
            mock.call(['fstrim', '--verbose', '/fake/']),
            mock.call(['umount', '/fake/'])
        ]
        self.assertListEqual(mock_exec_sudo.call_args_list, cmd_sequence)
