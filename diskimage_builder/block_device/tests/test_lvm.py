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

import copy
import logging
import mock

import diskimage_builder.block_device.tests.test_config as tc

from diskimage_builder.block_device.blockdevice import BlockDeviceState
from diskimage_builder.block_device.config import config_tree_to_graph
from diskimage_builder.block_device.config import create_graph
from diskimage_builder.block_device.exception import \
    BlockDeviceSetupException
from diskimage_builder.block_device.level0.localloop import LocalLoopNode
from diskimage_builder.block_device.level1.lvm import LVMNode
from diskimage_builder.block_device.level1.lvm import LVMPlugin
from diskimage_builder.block_device.level1.lvm import LvsNode
from diskimage_builder.block_device.level1.lvm import PvsNode
from diskimage_builder.block_device.level1.lvm import VgsNode
from diskimage_builder.block_device.level1.partitioning import PartitionNode

logger = logging.getLogger(__name__)


class TestLVM(tc.TestGraphGeneration):
    def test_lvm_tree_to_graph(self):
        # equivalence of tree-based to graph-based config
        tree = self.load_config_file('lvm_tree.yaml')
        graph = self.load_config_file('lvm_graph.yaml')
        parsed_graph = config_tree_to_graph(tree)
        self.assertItemsEqual(parsed_graph, graph)

    def test_lvm_invalid_config(self):
        # test some invalid config paths
        config = self.load_config_file('lvm_graph.yaml')
        lvm_config = config[2]['lvm']

        bad_config = copy.deepcopy(lvm_config)
        bad_config['vgs'][0]['base'] = ['invalid_pv']
        self.assertRaisesRegex(BlockDeviceSetupException,
                               "base:invalid_pv in vgs does not match "
                               "a valid pvs",
                               LVMPlugin, bad_config, {}, {})

        bad_config = copy.deepcopy(lvm_config)
        bad_config['lvs'][0]['base'] = ['invalid_vg']
        self.assertRaisesRegex(BlockDeviceSetupException,
                               r"base:\['invalid_vg'\] in lvs does not match "
                               r"a valid vg",
                               LVMPlugin, bad_config, {}, {})

        bad_config = copy.deepcopy(lvm_config)
        del(bad_config['lvs'][0]['size'])
        self.assertRaisesRegex(BlockDeviceSetupException,
                               "Missing 'size' or 'extents' in lvs config",
                               LVMPlugin, bad_config, {}, {})

    @mock.patch('diskimage_builder.block_device.level1.lvm.exec_sudo')
    def test_lvm_multi_pv(self, mock_exec_sudo):
        # Test the command-sequence for a more complicated LVM setup
        tree = self.load_config_file('lvm_tree_multiple_pv.yaml')
        config = config_tree_to_graph(tree)

        state = BlockDeviceState()

        graph, call_order = create_graph(config, self.fake_default_config,
                                         state)

        # XXX: todo; test call_order.  Make sure PV's come before, VG;
        # VG before LV, and that mounts/etc happen afterwards.

        # Fake state for the two PV's specified by this config
        state['blockdev'] = {}
        state['blockdev']['root'] = {}
        state['blockdev']['root']['device'] = '/dev/fake/root'
        state['blockdev']['data'] = {}
        state['blockdev']['data']['device'] = '/dev/fake/data'

        for node in call_order:
            # XXX: This has not mocked out the "lower" layers of
            # creating the devices, which we're assuming works OK, nor
            # the upper layers.
            if isinstance(node, (LVMNode, PvsNode,
                                 VgsNode, LvsNode)):
                # only the LVMNode actually does anything here...
                node.create()

        # ensure the sequence of calls correctly setup the devices
        cmd_sequence = [
            # create the pv's on the faked out block devices
            mock.call(['pvcreate', '/dev/fake/root', '--force']),
            mock.call(['pvcreate', '/dev/fake/data', '--force']),
            # create a volume called "vg" out of these two pv's
            mock.call(['vgcreate', 'vg',
                       '/dev/fake/root', '/dev/fake/data', '--force']),
            # create a bunch of lv's on vg
            mock.call(['lvcreate', '--name', 'lv_root', '-L', '1800M', 'vg']),
            mock.call(['lvcreate', '--name', 'lv_tmp', '-L', '100M', 'vg']),
            mock.call(['lvcreate', '--name', 'lv_var', '-L', '500M', 'vg']),
            mock.call(['lvcreate', '--name', 'lv_log', '-L', '100M', 'vg']),
            mock.call(['lvcreate', '--name', 'lv_audit', '-L', '100M', 'vg']),
            mock.call(['lvcreate', '--name', 'lv_home', '-L', '200M', 'vg'])]

        self.assertEqual(mock_exec_sudo.call_count, len(cmd_sequence))
        mock_exec_sudo.assert_has_calls(cmd_sequence)

        # Ensure the correct LVM state was preserved
        blockdev_state = {
            'data': {'device': '/dev/fake/data'},
            'root': {'device': '/dev/fake/root'},
            'lv_audit': {
                'device': '/dev/mapper/vg-lv_audit',
                'extents': None,
                'opts': None,
                'size': '100M',
                'vgs': 'vg'
            },
            'lv_home': {
                'device': '/dev/mapper/vg-lv_home',
                'extents': None,
                'opts': None,
                'size': '200M',
                'vgs': 'vg'
            },
            'lv_log': {
                'device': '/dev/mapper/vg-lv_log',
                'extents': None,
                'opts': None,
                'size': '100M',
                'vgs': 'vg'
            },
            'lv_root': {
                'device': '/dev/mapper/vg-lv_root',
                'extents': None,
                'opts': None,
                'size': '1800M',
                'vgs': 'vg'
            },
            'lv_tmp': {
                'device': '/dev/mapper/vg-lv_tmp',
                'extents': None,
                'opts': None,
                'size': '100M',
                'vgs': 'vg'
            },
            'lv_var': {
                'device': '/dev/mapper/vg-lv_var',
                'extents': None,
                'opts': None,
                'size': '500M',
                'vgs': 'vg'
            },
        }

        # state.debug_dump()
        self.assertDictEqual(state['blockdev'], blockdev_state)

        # XXX: mount ordering?  fs creation?

    def test_lvm_multi_pv_vg(self):
        # Test the command-sequence for a more complicated LVM setup
        tree = self.load_config_file('lvm_tree_multiple_pv_vg.yaml')
        config = config_tree_to_graph(tree)

        state = BlockDeviceState()

        graph, call_order = create_graph(config, self.fake_default_config,
                                         state)

        # XXX: todo; test call_order.  Make sure PV's come before, VG;
        # VG before LV, and that mounts/etc happen afterwards.

        # Fake state for the two PV's specified by this config
        state['blockdev'] = {}
        state['blockdev']['root'] = {}
        state['blockdev']['root']['device'] = '/dev/fake/root'
        state['blockdev']['data'] = {}
        state['blockdev']['data']['device'] = '/dev/fake/data'

        # We mock patch this ... it's just a little long!
        exec_sudo = 'diskimage_builder.block_device.level1.lvm.exec_sudo'

        #
        # Creation test
        #
        with mock.patch(exec_sudo) as mock_exec_sudo:

            for node in call_order:
                # XXX: This has not mocked out the "lower" layers of
                # creating the devices, which we're assuming works OK, nor
                # the upper layers.
                if isinstance(node, (LVMNode, PvsNode,
                                     VgsNode, LvsNode)):
                    # only the PvsNode actually does anything here...
                    node.create()

            # ensure the sequence of calls correctly setup the devices
            cmd_sequence = [
                # create the pv's on the faked out block devices
                mock.call(['pvcreate', '/dev/fake/root', '--force']),
                mock.call(['pvcreate', '/dev/fake/data', '--force']),
                # create a volume called "vg" out of these two pv's
                mock.call(['vgcreate', 'vg1',
                           '/dev/fake/root', '--force']),
                mock.call(['vgcreate', 'vg2',
                           '/dev/fake/data', '--force']),
                # create a bunch of lv's on vg
                mock.call(['lvcreate', '--name', 'lv_root',
                           '-L', '1800M', 'vg1']),
                mock.call(['lvcreate', '--name', 'lv_tmp',
                           '-L', '100M', 'vg1']),
                mock.call(['lvcreate', '--name', 'lv_var',
                           '-L', '500M', 'vg2']),
                mock.call(['lvcreate', '--name', 'lv_log',
                           '-L', '100M', 'vg2']),
                mock.call(['lvcreate', '--name', 'lv_audit',
                           '-L', '100M', 'vg2']),
                mock.call(['lvcreate', '--name', 'lv_home',
                           '-L', '200M', 'vg2'])]

            self.assertListEqual(mock_exec_sudo.call_args_list,
                                 cmd_sequence)

            # Ensure the correct LVM state was preserved
            blockdev_state = {
                'data': {'device': '/dev/fake/data'},
                'root': {'device': '/dev/fake/root'},
                'lv_audit': {
                    'device': '/dev/mapper/vg2-lv_audit',
                    'extents': None,
                    'opts': None,
                    'size': '100M',
                    'vgs': 'vg2'
                },
                'lv_home': {
                    'device': '/dev/mapper/vg2-lv_home',
                    'extents': None,
                    'opts': None,
                    'size': '200M',
                    'vgs': 'vg2'
                },
                'lv_log': {
                    'device': '/dev/mapper/vg2-lv_log',
                    'extents': None,
                    'opts': None,
                    'size': '100M',
                    'vgs': 'vg2'
                },
                'lv_root': {
                    'device': '/dev/mapper/vg1-lv_root',
                    'extents': None,
                    'opts': None,
                    'size': '1800M',
                    'vgs': 'vg1'
                },
                'lv_tmp': {
                    'device': '/dev/mapper/vg1-lv_tmp',
                    'extents': None,
                    'opts': None,
                    'size': '100M',
                    'vgs': 'vg1'
                },
                'lv_var': {
                    'device': '/dev/mapper/vg2-lv_var',
                    'extents': None,
                    'opts': None,
                    'size': '500M',
                    'vgs': 'vg2'
                },
            }

            # state.debug_dump()
            self.assertDictEqual(state['blockdev'], blockdev_state)

        #
        # Umount test
        #
        with mock.patch(exec_sudo) as mock_exec_sudo, \
             mock.patch('tempfile.NamedTemporaryFile') as mock_temp, \
             mock.patch('os.unlink'):

            # each call to tempfile.NamedTemporaryFile will return a
            # new mock with a unique filename, which we store in
            # tempfiles
            tempfiles = []

            def new_tempfile(*args, **kwargs):
                n = '/tmp/files%s' % len(tempfiles)
                # trap! note mock.Mock(name = n) doesn't work like you
                # think it would, since mock has a name attribute.
                # That's why we override it with the configure_mock
                # (this is mentioned in mock documentation if you read
                # it :)
                r = mock.Mock()
                r.configure_mock(name=n)
                tempfiles.append(n)
                return r
            mock_temp.side_effect = new_tempfile

            def run_it(phase):
                reverse_order = reversed(call_order)
                for node in reverse_order:
                    if isinstance(node, (LVMNode, PvsNode, VgsNode, LvsNode)):
                        getattr(node, phase)()
                    else:
                        logger.debug("Skipping node for test: %s", node)

            run_it('umount')
            run_it('cleanup')

            cmd_sequence = [
                # delete the lv's
                mock.call(['lvchange', '-an', '/dev/vg1/lv_root']),
                mock.call(['lvchange', '-an', '/dev/vg1/lv_tmp']),
                mock.call(['lvchange', '-an', '/dev/vg2/lv_var']),
                mock.call(['lvchange', '-an', '/dev/vg2/lv_log']),
                mock.call(['lvchange', '-an', '/dev/vg2/lv_audit']),
                mock.call(['lvchange', '-an', '/dev/vg2/lv_home']),
                # delete the vg's
                mock.call(['vgchange', '-an', 'vg1']),
                mock.call(['vgchange', '-an', 'vg2']),
                mock.call(['udevadm', 'settle']),
                mock.call(['pvscan', '--cache']),
            ]

            self.assertListEqual(mock_exec_sudo.call_args_list, cmd_sequence)

    def test_lvm_spanned_vg(self):

        # Test when a volume group spans some partitions

        tree = self.load_config_file('lvm_tree_spanned_vg.yaml')
        config = config_tree_to_graph(tree)

        state = BlockDeviceState()

        graph, call_order = create_graph(config, self.fake_default_config,
                                         state)

        # XXX: todo; test call_order.  Make sure PV's come before, VG;
        # VG before LV, and that mounts/etc happen afterwards.

        # Fake state for the two PV's specified by this config
        state['blockdev'] = {}
        state['blockdev']['root'] = {}
        state['blockdev']['root']['device'] = '/dev/fake/root'
        state['blockdev']['data1'] = {}
        state['blockdev']['data1']['device'] = '/dev/fake/data1'
        state['blockdev']['data2'] = {}
        state['blockdev']['data2']['device'] = '/dev/fake/data2'

        # We mock patch this ... it's just a little long!
        exec_sudo = 'diskimage_builder.block_device.level1.lvm.exec_sudo'

        #
        # Creation test
        #
        with mock.patch(exec_sudo) as mock_exec_sudo:

            for node in call_order:
                # XXX: This has not mocked out the "lower" layers of
                # creating the devices, which we're assuming works OK, nor
                # the upper layers.
                if isinstance(node, (LVMNode, PvsNode, VgsNode, LvsNode)):
                    # only the LVMNode actually does anything here...
                    node.create()

            # ensure the sequence of calls correctly setup the devices
            cmd_sequence = [
                # create the pv's on the faked out block devices
                mock.call(['pvcreate', '/dev/fake/root', '--force']),
                mock.call(['pvcreate', '/dev/fake/data1', '--force']),
                mock.call(['pvcreate', '/dev/fake/data2', '--force']),
                # create a root and a data volume, with the data volume
                # spanning data1 & data2
                mock.call(['vgcreate', 'vg_root',
                           '/dev/fake/root', '--force']),
                mock.call(['vgcreate', 'vg_data',
                           '/dev/fake/data1', '/dev/fake/data2', '--force']),
                # create root and data volume
                mock.call(['lvcreate', '--name', 'lv_root',
                           '-L', '1800M', 'vg_root']),
                mock.call(['lvcreate', '--name', 'lv_data',
                           '-L', '2G', 'vg_data'])
            ]

            self.assertListEqual(mock_exec_sudo.call_args_list,
                                 cmd_sequence)

        with mock.patch(exec_sudo) as mock_exec_sudo, \
             mock.patch('tempfile.NamedTemporaryFile') as mock_temp, \
             mock.patch('os.unlink'):

            # see above ...
            tempfiles = []

            def new_tempfile(*args, **kwargs):
                n = '/tmp/files%s' % len(tempfiles)
                r = mock.Mock()
                r.configure_mock(name=n)
                tempfiles.append(n)
                return r
            mock_temp.side_effect = new_tempfile

            def run_it(phase):
                reverse_order = reversed(call_order)
                for node in reverse_order:
                    if isinstance(node, (LVMNode, PvsNode, VgsNode, LvsNode)):
                        getattr(node, phase)()
                    else:
                        logger.debug("Skipping node for test: %s", node)

            run_it('umount')
            run_it('cleanup')

            cmd_sequence = [
                # deactivate lv's
                mock.call(['lvchange', '-an', '/dev/vg_root/lv_root']),
                mock.call(['lvchange', '-an', '/dev/vg_data/lv_data']),

                # deactivate vg's
                mock.call(['vgchange', '-an', 'vg_root']),
                mock.call(['vgchange', '-an', 'vg_data']),

                mock.call(['udevadm', 'settle']),
                mock.call(['pvscan', '--cache']),
            ]

            self.assertListEqual(mock_exec_sudo.call_args_list, cmd_sequence)

    def test_lvm_multiple_partitions(self):
        # Test the command-sequence for several partitions, one containing
        # volumes on it
        tree = self.load_config_file('lvm_tree_multiple_partitions.yaml')
        config = config_tree_to_graph(tree)

        state = BlockDeviceState()

        graph, call_order = create_graph(config, self.fake_default_config,
                                         state)

        # Fake state for the partitions on this config
        state['blockdev'] = {}
        state['blockdev']['image0'] = {}
        state['blockdev']['image0']['device'] = '/dev/fake/image0'
        state['blockdev']['image0']['image'] = 'image'
        state['blockdev']['root'] = {}
        state['blockdev']['root']['device'] = '/dev/fake/root'
        state['blockdev']['ESP'] = {}
        state['blockdev']['ESP']['device'] = '/dev/fake/ESP'
        state['blockdev']['BSP'] = {}
        state['blockdev']['BSP']['device'] = '/dev/fake/BSP'

        #
        # Creation test
        #

        # We mock out the following exec_sudo and other related calls
        # calls for the layers we are testing.
        exec_sudo_lvm = 'diskimage_builder.block_device.level1.lvm.exec_sudo'
        exec_sudo_part = ('diskimage_builder.block_device.'
                          'level1.partitioning.exec_sudo')
        exec_sudo_loop = ('diskimage_builder.block_device.'
                          'level0.localloop.exec_sudo')
        image_create = ('diskimage_builder.block_device.level0.'
                        'localloop.LocalLoopNode.create')
        size_of_block = ('diskimage_builder.block_device.level1.'
                         'partitioning.Partitioning._size_of_block_dev')
        create_mbr = ('diskimage_builder.block_device.level1.'
                      'partitioning.Partitioning._create_mbr')

        manager = mock.MagicMock()
        with mock.patch(exec_sudo_lvm) as mock_sudo_lvm, \
             mock.patch(exec_sudo_part) as mock_sudo_part, \
             mock.patch(exec_sudo_loop) as mock_sudo_loop, \
             mock.patch(image_create) as mock_image_create, \
             mock.patch(size_of_block) as mock_size_of_block, \
             mock.patch(create_mbr) as mock_create_mbr:

            manager.attach_mock(mock_sudo_lvm, 'sudo_lvm')
            manager.attach_mock(mock_sudo_part, 'sudo_part')
            manager.attach_mock(mock_sudo_loop, 'sudo_loop')
            manager.attach_mock(mock_image_create, 'image_create')
            manager.attach_mock(mock_size_of_block, 'size_of_block')
            manager.attach_mock(mock_create_mbr, 'create_mbr')

            for node in call_order:
                # We're just keeping this to the partition setup and
                # LVM creation; i.e. skipping mounting, mkfs, etc.
                if isinstance(node, (LVMNode, PvsNode,
                                     VgsNode, LvsNode,
                                     LocalLoopNode, PartitionNode)):
                    node.create()
                else:
                    logger.debug("Skipping node for test: %s", node)

            cmd_sequence = [
                # create the underlying block device
                mock.call.image_create(),
                mock.call.size_of_block('image'),
                # write out partition table
                mock.call.create_mbr(),
                # now mount partitions
                mock.call.sudo_part(['sync']),
                mock.call.sudo_part(['kpartx', '-avs', '/dev/fake/image0']),
                # now create lvm environment
                mock.call.sudo_lvm(['pvcreate', '/dev/fake/root', '--force']),
                mock.call.sudo_lvm(
                    ['vgcreate', 'vg', '/dev/fake/root', '--force']),
                mock.call.sudo_lvm(
                    ['lvcreate', '--name', 'lv_root', '-l', '28%VG', 'vg']),
                mock.call.sudo_lvm(
                    ['lvcreate', '--name', 'lv_tmp', '-l', '4%VG', 'vg']),
                mock.call.sudo_lvm(
                    ['lvcreate', '--name', 'lv_var', '-l', '40%VG', 'vg']),
                mock.call.sudo_lvm(
                    ['lvcreate', '--name', 'lv_log', '-l', '23%VG', 'vg']),
                mock.call.sudo_lvm(
                    ['lvcreate', '--name', 'lv_audit', '-l', '4%VG', 'vg']),
                mock.call.sudo_lvm(
                    ['lvcreate', '--name', 'lv_home', '-l', '1%VG', 'vg']),
            ]
            manager.assert_has_calls(cmd_sequence)

        #
        # Umount/cleanup test
        #
        manager = mock.MagicMock()
        with mock.patch(exec_sudo_lvm) as mock_sudo_lvm, \
             mock.patch(exec_sudo_part) as mock_sudo_part, \
             mock.patch(exec_sudo_loop) as mock_sudo_loop:

            manager.attach_mock(mock_sudo_lvm, 'sudo_lvm')
            manager.attach_mock(mock_sudo_part, 'sudo_part')
            manager.attach_mock(mock_sudo_loop, 'sudo_loop')

            def run_it(phase):
                reverse_order = reversed(call_order)
                for node in reverse_order:
                    if isinstance(node, (LVMNode, PvsNode,
                                         VgsNode, LvsNode,
                                         LocalLoopNode, PartitionNode)):
                        getattr(node, phase)()
                    else:
                        logger.debug("Skipping node for test: %s", node)

            run_it('umount')
            run_it('cleanup')

            cmd_sequence = [
                # deactivate LVM first
                mock.call.sudo_lvm(['lvchange', '-an', '/dev/vg/lv_root']),
                mock.call.sudo_lvm(['lvchange', '-an', '/dev/vg/lv_tmp']),
                mock.call.sudo_lvm(['lvchange', '-an', '/dev/vg/lv_var']),
                mock.call.sudo_lvm(['lvchange', '-an', '/dev/vg/lv_log']),
                mock.call.sudo_lvm(['lvchange', '-an', '/dev/vg/lv_audit']),
                mock.call.sudo_lvm(['lvchange', '-an', '/dev/vg/lv_home']),
                mock.call.sudo_lvm(['vgchange', '-an', 'vg']),
                mock.call.sudo_lvm(['udevadm', 'settle']),
                # now remove partitions (note has to happen after lvm removal)
                mock.call.sudo_part(['kpartx', '-d', '/dev/fake/image0']),
                # now remove loopback device
                mock.call.sudo_loop(['losetup', '-d', '/dev/fake/image0']),
                # now final LVM cleanup call
                mock.call.sudo_lvm(['pvscan', '--cache']),
            ]

            manager.assert_has_calls(cmd_sequence)
