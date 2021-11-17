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
import imp
import mock
import os
from oslotest import base

module_path = (os.path.dirname(os.path.realpath(__file__)) +
               '/../static/usr/local/sbin/growvols')
growvols = imp.load_source('growvols', module_path)

# output of lsblk -Po kname,pkname,name,label,type,fstype,mountpoint
LSBLK = """KNAME="sda" PKNAME="" NAME="sda" LABEL="" TYPE="disk" FSTYPE="" MOUNTPOINT=""
KNAME="sda1" PKNAME="sda" NAME="sda1" LABEL="MKFS_ESP" TYPE="part" FSTYPE="vfat" MOUNTPOINT="/boot/efi"
KNAME="sda2" PKNAME="sda" NAME="sda2" LABEL="" TYPE="part" FSTYPE="" MOUNTPOINT=""
KNAME="sda3" PKNAME="sda" NAME="sda3" LABEL="" TYPE="part" FSTYPE="LVM2_member" MOUNTPOINT=""
KNAME="sda4" PKNAME="sda" NAME="sda4" LABEL="config-2" TYPE="part" FSTYPE="iso9660" MOUNTPOINT=""
KNAME="dm-0" PKNAME="sda3" NAME="vg-lv_root" LABEL="img-rootfs" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/"
KNAME="dm-1" PKNAME="sda3" NAME="vg-lv_tmp" LABEL="fs_tmp" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/tmp"
KNAME="dm-2" PKNAME="sda3" NAME="vg-lv_var" LABEL="fs_var" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/var"
KNAME="dm-3" PKNAME="sda3" NAME="vg-lv_home" LABEL="fs_home" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/home"
""" # noqa

DEVICES = [{
    "FSTYPE": "",
    "KNAME": "sda",
    "LABEL": "",
    "MOUNTPOINT": "",
    "NAME": "sda",
    "PKNAME": "",
    "TYPE": "disk",
}, {
    "FSTYPE": "vfat",
    "KNAME": "sda1",
    "LABEL": "MKFS_ESP",
    "MOUNTPOINT": "/boot/efi",
    "NAME": "sda1",
    "PKNAME": "sda",
    "TYPE": "part",
}, {
    "FSTYPE": "",
    "KNAME": "sda2",
    "LABEL": "",
    "MOUNTPOINT": "",
    "NAME": "sda2",
    "PKNAME": "sda",
    "TYPE": "part",
}, {
    "FSTYPE": "LVM2_member",
    "KNAME": "sda3",
    "LABEL": "",
    "MOUNTPOINT": "",
    "NAME": "sda3",
    "PKNAME": "sda",
    "TYPE": "part",
}, {
    "FSTYPE": "iso9660",
    "KNAME": "sda4",
    "LABEL": "config-2",
    "MOUNTPOINT": "",
    "NAME": "sda4",
    "PKNAME": "sda",
    "TYPE": "part",
}, {
    "FSTYPE": "xfs",
    "KNAME": "dm-0",
    "LABEL": "img-rootfs",
    "MOUNTPOINT": "/",
    "NAME": "vg-lv_root",
    "PKNAME": "sda3",
    "TYPE": "lvm",
}, {
    "FSTYPE": "xfs",
    "KNAME": "dm-1",
    "LABEL": "fs_tmp",
    "MOUNTPOINT": "/tmp",
    "NAME": "vg-lv_tmp",
    "PKNAME": "sda3",
    "TYPE": "lvm",
}, {
    "FSTYPE": "xfs",
    "KNAME": "dm-2",
    "LABEL": "fs_var",
    "MOUNTPOINT": "/var",
    "NAME": "vg-lv_var",
    "PKNAME": "sda3",
    "TYPE": "lvm",
}, {
    "FSTYPE": "xfs",
    "KNAME": "dm-3",
    "LABEL": "fs_home",
    "MOUNTPOINT": "/home",
    "NAME": "vg-lv_home",
    "PKNAME": "sda3",
    "TYPE": "lvm",
}]

# output of sgdisk --first-aligned-in-largest --end-of-largest /dev/sda
SECTOR_START = 79267840
SECTOR_END = 488265727
SGDISK_LARGEST = "%s\n%s\n" % (SECTOR_START, SECTOR_END)

# output of vgs --noheadings --options vg_name
VGS = "  vg\n"


class TestGrowvols(base.BaseTestCase):

    def test_printable_cmd(self):
        self.assertEqual(
            "foo --thing 'bar baz'",
            growvols.printable_cmd(['foo', '--thing', "bar baz"])
        )

    def test_convert_bytes(self):
        self.assertEqual('100B', growvols.convert_bytes(100))
        self.assertEqual('1KB', growvols.convert_bytes(1000))
        self.assertEqual('2MB', growvols.convert_bytes(2000000))
        self.assertEqual('3GB', growvols.convert_bytes(3000000000))
        self.assertEqual('4TB', growvols.convert_bytes(4000000000000))

    @mock.patch('subprocess.Popen')
    def test_execute(self, mock_popen):
        mock_process = mock.Mock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = ('did the thing', '')
        mock_popen.return_value = mock_process

        result = growvols.execute(['do', 'the', 'thing'])
        self.assertEqual('did the thing', result)

        mock_process.returncode = 1
        mock_process.communicate.return_value = ('', 'ouch')

        e = self.assertRaises(Exception, growvols.execute,
                              ['do', 'the', 'thing'])
        self.assertIn('ouch', str(e))

    def test_parse_shell_vars(self):
        devices = list(growvols.parse_shell_vars(LSBLK))
        self.assertEqual(DEVICES, devices)

    def test_find_device(self):
        sda = {
            "FSTYPE": "",
            "KNAME": "sda",
            "LABEL": "",
            "MOUNTPOINT": "",
            "NAME": "sda",
            "PKNAME": "",
            "TYPE": "disk",
        }
        fs_home = {
            "FSTYPE": "xfs",
            "KNAME": "dm-3",
            "LABEL": "fs_home",
            "MOUNTPOINT": "/home",
            "NAME": "vg-lv_home",
            "PKNAME": "sda3",
            "TYPE": "lvm",
        }
        self.assertEqual(
            sda, growvols.find_device(DEVICES, 'NAME', 'sda'))
        self.assertEqual(
            fs_home,
            growvols.find_device(
                DEVICES, ['KNAME', 'NAME'], 'vg-lv_home'))
        self.assertEqual(
            fs_home,
            growvols.find_device(
                DEVICES, ['KNAME', 'NAME'], 'dm-3'))
        self.assertIsNone(
            growvols.find_device(
                DEVICES, ['KNAME', 'NAME'], 'asdf'))

    def test_find_disk(self):
        devices = list(growvols.parse_shell_vars(LSBLK))
        opts = mock.Mock()
        opts.device = None
        sda = growvols.find_device(devices, 'NAME', 'sda')

        # discover via MOUNTPOINT /
        self.assertEqual(sda, growvols.find_disk(opts, devices))

        # fetch sda
        opts.device = 'sda'
        self.assertEqual(sda, growvols.find_disk(opts, devices))

        # delete sda3, so can't find relationship
        # from MOUNTPOINT / to sda
        opts.device = None
        devices = [d for d in devices if d['NAME'] != 'sda3']
        e = self.assertRaises(Exception, growvols.find_disk, opts, devices)
        self.assertEqual('Could not detect disk device', str(e))

        # no sdb
        opts.device = 'sdb'
        e = self.assertRaises(Exception, growvols.find_disk, opts, devices)
        self.assertEqual('Could not find specified --device: sdb', str(e))

        # sda is not TYPE disk
        sda['TYPE'] = 'dissed'
        opts.device = 'sda'
        e = self.assertRaises(Exception, growvols.find_disk, opts, devices)
        self.assertEqual('Expected a device with TYPE="disk", got: dissed',
                         str(e))

    @mock.patch('growvols.execute')
    def test_find_space(self, mock_execute):
        mock_execute.return_value = SGDISK_LARGEST
        sector_start, sector_end, size_sectors = growvols.find_space(
            'sda')
        self.assertEqual(SECTOR_START, sector_start)
        self.assertEqual(SECTOR_END, sector_end)
        self.assertEqual(SECTOR_END - SECTOR_START, size_sectors)
        mock_execute.assert_called_once_with([
            'sgdisk',
            '--first-aligned-in-largest',
            '--end-of-largest',
            '/dev/sda'])

    @mock.patch('growvols.execute')
    def test_find_devices(self, mock_execute):
        mock_execute.return_value = LSBLK
        self.assertEqual(DEVICES, growvols.find_devices())
        mock_execute.assert_called_once_with([
            'lsblk',
            '-Po',
            'kname,pkname,name,label,type,fstype,mountpoint'])

    @mock.patch('growvols.execute')
    def test_find_group(self, mock_execute):
        mock_execute.return_value = VGS
        opts = mock.Mock()
        opts.group = None
        self.assertEqual('vg', growvols.find_group(opts))
        mock_execute.assert_called_once_with([
            'vgs', '--noheadings', '--options', 'vg_name'])

        # no volume groups
        mock_execute.return_value = "\n"
        e = self.assertRaises(Exception, growvols.find_group, opts)
        self.assertEqual('No volume groups found', str(e))

        # multiple volume groups
        mock_execute.return_value = "  vg\nvg2\nvg3"
        e = self.assertRaises(Exception, growvols.find_group, opts)
        self.assertEqual('More than one volume group, specify one to '
                         'use with --group: vg, vg2, vg3', str(e))

        # multiple volume groups with explicit group argument
        opts.group = 'vg'
        self.assertEqual('vg', growvols.find_group(opts))

        # no such group
        opts.group = 'novg'
        e = self.assertRaises(Exception, growvols.find_group, opts)
        self.assertEqual('Could not find specified --group: novg', str(e))

    def test_find_next_partnum(self):
        self.assertEqual(5, growvols.find_next_partnum(DEVICES, 'sda'))
        self.assertEqual(1, growvols.find_next_partnum(DEVICES, 'sdb'))

    def test_find_next_device_name(self):
        devices = list(growvols.parse_shell_vars(LSBLK))

        # Use SATA etc device naming
        self.assertEqual(
            'sda5',
            growvols.find_next_device_name(devices, 'sda', 5))

        # No partitions
        e = self.assertRaises(Exception, growvols.find_next_device_name,
                              devices, 'sdb', 1)
        self.assertEqual(
            'Could not find partition naming scheme for sdb', str(e))

        # Use NVMe device naming
        for i in (1, 2, 3, 4):
            d = growvols.find_device(devices, 'KNAME', 'sda%s' % i)
            d['KNAME'] = 'nvme0p%s' % i
        self.assertEqual(
            'nvme0p5',
            growvols.find_next_device_name(devices, 'nvme0', 5))

    def test_amount_unit_to_extent(self):
        one_m = growvols.UNIT_BYTES['MiB']
        four_m = one_m * 4
        one_g = growvols.UNIT_BYTES['GiB']
        ten_g = one_g * 10
        forty_g = ten_g * 4
        fidy_g = ten_g * 5

        # invalid amounts
        self.assertRaises(Exception, growvols.amount_unit_to_extent,
                          '100', one_g, one_g)
        self.assertRaises(Exception, growvols.amount_unit_to_extent,
                          '100B', one_g, one_g)
        self.assertRaises(Exception, growvols.amount_unit_to_extent,
                          '100%%', one_g, one_g)
        self.assertRaises(Exception, growvols.amount_unit_to_extent,
                          '100TiB', one_g, one_g)
        self.assertRaises(Exception, growvols.amount_unit_to_extent,
                          'i100MB', one_g, one_g)

        # GiB amount
        self.assertEqual(
            (ten_g, forty_g),
            growvols.amount_unit_to_extent('10GiB', fidy_g, fidy_g)
        )

        # percentage amount
        self.assertEqual(
            (ten_g, forty_g),
            growvols.amount_unit_to_extent('20%', fidy_g, fidy_g)
        )

        # not enough space left
        self.assertEqual(
            (0, one_m),
            growvols.amount_unit_to_extent('20%', fidy_g, one_m)
        )

        # exactly one extent
        self.assertEqual(
            (four_m, fidy_g - four_m),
            growvols.amount_unit_to_extent('4MiB', fidy_g, fidy_g)
        )

        # under one extent is zero
        self.assertEqual(
            (0, fidy_g),
            growvols.amount_unit_to_extent('3MiB', fidy_g, fidy_g)
        )

        # just over one extent is one extent
        self.assertEqual(
            (four_m, fidy_g - four_m),
            growvols.amount_unit_to_extent('5MiB', fidy_g, fidy_g)
        )

    def test_find_grow_vols(self):
        one_g = growvols.UNIT_BYTES['GiB']
        ten_g = one_g * 10
        fidy_g = ten_g * 5

        opts = mock.Mock()

        # buy default, assign all to /
        opts.grow_vols = ['']
        self.assertEqual(
            {'/dev/lv/lv_root': fidy_g},
            growvols.find_grow_vols(opts, DEVICES, 'lv', fidy_g)
        )

        # assign to /home, /var, remainder to /
        opts.grow_vols = ['/home=20%', 'fs_var=40%']
        self.assertEqual(
            {
                '/dev/lv/lv_home': ten_g,
                '/dev/lv/lv_var': ten_g * 2,
                '/dev/lv/lv_root': ten_g * 2
            },
            growvols.find_grow_vols(opts, DEVICES, 'lv', fidy_g)
        )

        # assign to /home, /var, /tmp by amount
        opts.grow_vols = ['/home=19GiB', 'fs_var=30GiB', '/tmp=1GiB']
        self.assertEqual(
            {
                '/dev/lv/lv_home': one_g * 19,
                '/dev/lv/lv_var': one_g * 30,
                '/dev/lv/lv_tmp': one_g
            },
            growvols.find_grow_vols(opts, DEVICES, 'lv', fidy_g)
        )

    @mock.patch('builtins.open', autospec=True)
    def test_find_sector_size(self, mock_open):
        mock_open.return_value.__enter__ = lambda s: s
        mock_open.return_value.__exit__ = mock.Mock()
        read_mock = mock_open.return_value.read
        read_mock.side_effect = ['512']

        # disk sdx exists
        self.assertEqual(512, growvols.find_sector_size('sdx'))

        # disk sdx doesn't exist
        mock_open.side_effect = FileNotFoundError
        self.assertRaises(FileNotFoundError, growvols.find_sector_size, 'sdx')

    @mock.patch('growvols.find_sector_size')
    @mock.patch('growvols.execute')
    def test_main(self, mock_execute, mock_sector_size):
        mock_sector_size.return_value = 512

        # noop, only discover block device info
        mock_execute.side_effect = [
            LSBLK,
            SGDISK_LARGEST,
            VGS,
        ]
        growvols.main(['growvols', '--noop'])
        mock_execute.assert_has_calls([
            mock.call(['lsblk', '-Po',
                       'kname,pkname,name,label,type,fstype,mountpoint']),
            mock.call(['sgdisk', '--first-aligned-in-largest',
                       '--end-of-largest', '/dev/sda']),
            mock.call(['vgs', '--noheadings', '--options', 'vg_name']),
        ])

        # no arguments, assign all to /
        mock_execute.reset_mock()
        mock_execute.side_effect = [
            LSBLK,
            SGDISK_LARGEST,
            VGS,
            '', '', '', '', '', ''
        ]
        growvols.main(['growvols', '--yes'])
        mock_execute.assert_has_calls([
            mock.call(['lsblk', '-Po',
                       'kname,pkname,name,label,type,fstype,mountpoint']),
            mock.call(['sgdisk', '--first-aligned-in-largest',
                       '--end-of-largest', '/dev/sda']),
            mock.call(['vgs', '--noheadings', '--options', 'vg_name']),
            mock.call(['sgdisk', '--new=5:79267840:488265727',
                       '--change-name=5:growvols', '/dev/sda']),
            mock.call(['partprobe']),
            mock.call(['pvcreate', '/dev/sda5']),
            mock.call(['vgextend', 'vg', '/dev/sda5']),
            mock.call(['lvextend', '--size', '+209404821504B',
                       '/dev/vg/lv_root', '/dev/sda5']),
            mock.call(['xfs_growfs', '/dev/vg/lv_root'])
        ])

        # assign to /home, /var, remainder to /
        mock_execute.reset_mock()
        mock_execute.side_effect = [
            LSBLK,
            SGDISK_LARGEST,
            VGS,
            '', '', '', '', '', '', '', '', '', ''
        ]
        growvols.main(['growvols', '--yes', '--group', 'vg',
                       '/home=20%', 'fs_var=40%'])
        mock_execute.assert_has_calls([
            mock.call(['lsblk', '-Po',
                       'kname,pkname,name,label,type,fstype,mountpoint']),
            mock.call(['sgdisk', '--first-aligned-in-largest',
                       '--end-of-largest', '/dev/sda']),
            mock.call(['vgs', '--noheadings', '--options', 'vg_name']),
            mock.call(['sgdisk', '--new=5:79267840:488265727',
                       '--change-name=5:growvols', '/dev/sda']),
            mock.call(['partprobe']),
            mock.call(['pvcreate', '/dev/sda5']),
            mock.call(['vgextend', 'vg', '/dev/sda5']),
            mock.call(['lvextend', '--size', '+41880125440B',
                       '/dev/vg/lv_home', '/dev/sda5']),
            mock.call(['lvextend', '--size', '+83760250880B',
                       '/dev/vg/lv_var', '/dev/sda5']),
            mock.call(['lvextend', '--size', '+83764445184B',
                       '/dev/vg/lv_root', '/dev/sda5']),
            mock.call(['xfs_growfs', '/dev/vg/lv_home']),
            mock.call(['xfs_growfs', '/dev/vg/lv_var']),
            mock.call(['xfs_growfs', '/dev/vg/lv_root']),
        ])

        # no space to grow, failed
        sector_start = 79267840
        sector_end = sector_start + 1024
        sgdisk_largest = "%s\n%s\n" % (sector_start, sector_end)
        mock_execute.side_effect = [
            LSBLK,
            sgdisk_largest,
            VGS,
        ]
        self.assertEqual(
            2,
            growvols.main(['growvols', '--exit-on-no-grow'])
        )

        # no space to grow, success
        mock_execute.side_effect = [
            LSBLK,
            sgdisk_largest,
            VGS,
        ]
        self.assertEqual(
            0,
            growvols.main(['growvols'])
        )
