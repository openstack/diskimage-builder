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
from diskimage_builder.block_device.level2.mkfs import FilesystemNode
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
    @mock.patch('diskimage_builder.block_device.level2.mkfs.exec_sudo',
                side_effect=_exec_sudo_log)
    def test_mfks_and_mount_order(self, mock_exec_sudo_mkfs,
                                  mock_exec_sudo_mount):
        # XXX: better mocking for the os.path.exists calls to avoid
        # failing if this exists.
        self.assertFalse(os.path.exists('/fake/'))

        # This is probably in order after graph creation, so ensure it
        # remains stable.  We test the mount and umount call sequences
        config = self.load_config_file('multiple_partitions_graph.yaml')
        state = {}
        graph, call_order = create_graph(config, self.fake_default_config,
                                         state)

        # Mocked block device state
        state['blockdev'] = {}
        state['blockdev']['root'] = {'device': '/dev/loopXp1/root'}
        state['blockdev']['var'] = {'device': '/dev/loopXp2/var'}
        state['blockdev']['var_log'] = {'device': '/dev/loopXp3/var_log'}

        for node in call_order:
            if isinstance(node, (FilesystemNode, MountPointNode)):
                node.create()
        for node in reversed(call_order):
            if isinstance(node, (FilesystemNode, MountPointNode)):
                node.umount()

        # ensure that partitions were mounted in order root->var->var/log
        self.assertListEqual(state['mount_order'], ['/', '/var', '/var/log'])

        # fs creation sequence (note we don't care about order of this
        # as they're all independent)
        cmd_sequence = [
            mock.call(['mkfs', '-t', 'xfs', '-L', 'mkfs_root',
                       '-m', 'uuid=root-uuid-1234',
                       '-q', '/dev/loopXp1/root']),
            mock.call(['mkfs', '-t', 'xfs', '-L', 'mkfs_var',
                       '-m', 'uuid=var-uuid-1234',
                       '-q', '/dev/loopXp2/var']),
            mock.call(['mkfs', '-t', 'vfat', '-n', 'VARLOG',
                       '/dev/loopXp3/var_log'])
        ]
        self.assertEqual(mock_exec_sudo_mkfs.call_count, len(cmd_sequence))
        mock_exec_sudo_mkfs.assert_has_calls(cmd_sequence, any_order=True)

        # Check mount sequence
        cmd_sequence = [
            # mount sequence
            mock.call(['mkdir', '-p', '/fake/']),
            mock.call(['mount', '/dev/loopXp1/root', '/fake/']),
            mock.call(['mkdir', '-p', '/fake/var']),
            mock.call(['mount', '/dev/loopXp2/var', '/fake/var']),
            mock.call(['mkdir', '-p', '/fake/var/log']),
            mock.call(['mount', '/dev/loopXp3/var_log', '/fake/var/log']),
            # umount sequence
            mock.call(['sync']),
            # note /fake/var/log is a vfs partition to make sure
            # we don't try to fstrim it
            mock.call(['umount', '/fake/var/log']),
            mock.call(['sync']),
            mock.call(['fstrim', '--verbose', '/fake/var']),
            mock.call(['umount', '/fake/var']),
            mock.call(['sync']),
            mock.call(['fstrim', '--verbose', '/fake/']),
            mock.call(['umount', '/fake/'])
        ]
        self.assertListEqual(mock_exec_sudo_mount.call_args_list, cmd_sequence)

    @mock.patch('diskimage_builder.block_device.level3.mount.exec_sudo',
                side_effect=_exec_sudo_log)
    def test_mount_order_unsorted(self, mock_exec_sudo):
        # As above, but this is out of order and gets sorted
        # so that root is mounted first (and skips the mkfs testing).
        config = self.load_config_file('lvm_tree_partition_ordering.yaml')
        parsed_graph = config_tree_to_graph(config)
        state = {}

        graph, call_order = create_graph(parsed_graph,
                                         self.fake_default_config,
                                         state)
        state['filesys'] = {
            'mkfs_root': {
                'device': '/dev/loopXp1',
                'fstype': 'xfs'
            },
            'mkfs_var': {
                'device': '/dev/loopXp2',
                'fstype': 'xfs',
            },
            'mkfs_boot': {
                'device': '/dev/loopXp3',
                'fstype': 'vfat',
            },
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
            mock.call(['mount', '/dev/loopXp1', '/fake/']),
            mock.call(['mkdir', '-p', '/fake/boot']),
            mock.call(['mount', '/dev/loopXp3', '/fake/boot']),
            mock.call(['mkdir', '-p', '/fake/var']),
            mock.call(['mount', '/dev/loopXp2', '/fake/var']),
            # umount sequence
            mock.call(['sync']),
            mock.call(['fstrim', '--verbose', '/fake/var']),
            mock.call(['umount', '/fake/var']),
            mock.call(['sync']),
            # no trim on vfat /fake/boot
            mock.call(['umount', '/fake/boot']),
            mock.call(['sync']),
            mock.call(['fstrim', '--verbose', '/fake/']),
            mock.call(['umount', '/fake/'])
        ]
        self.assertListEqual(mock_exec_sudo.call_args_list, cmd_sequence)
