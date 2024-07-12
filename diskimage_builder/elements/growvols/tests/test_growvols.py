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
import copy
import importlib
import os
import sys
from unittest import mock

from oslotest import base


importlib.machinery.SOURCE_SUFFIXES.append('')
file_path = (os.path.dirname(os.path.realpath(__file__)) +
             '/../static/usr/local/sbin/growvols')
spec = importlib.util.spec_from_file_location('growvols', file_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
sys.modules['growvols'] = module
growvols = module
importlib.machinery.SOURCE_SUFFIXES.pop()

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

# output of multipath lsblk
LSBLK_MULTIPATH = """KNAME="sda" PKNAME="" NAME="sda" LABEL="" TYPE="disk" FSTYPE="mpath_member" MOUNTPOINT=""
KNAME="dm-0" PKNAME="sda" NAME="mpatha" LABEL="" TYPE="mpath" FSTYPE="" MOUNTPOINT=""
KNAME="dm-1" PKNAME="dm-0" NAME="mpatha1" LABEL="MKFS_ESP" TYPE="part" FSTYPE="vfat" MOUNTPOINT="/boot/efi"
KNAME="dm-2" PKNAME="dm-0" NAME="mpatha2" LABEL="" TYPE="part" FSTYPE="" MOUNTPOINT=""
KNAME="dm-3" PKNAME="dm-0" NAME="mpatha3" LABEL="mkfs_boot" TYPE="part" FSTYPE="ext4" MOUNTPOINT="/boot"
KNAME="dm-4" PKNAME="dm-0" NAME="mpatha4" LABEL="" TYPE="part" FSTYPE="LVM2_member" MOUNTPOINT=""
KNAME="dm-6" PKNAME="dm-4" NAME="vg-lv_thinpool_tmeta" LABEL="" TYPE="lvm" FSTYPE="" MOUNTPOINT=""
KNAME="dm-8" PKNAME="dm-6" NAME="vg-lv_thinpool-tpool" LABEL="" TYPE="lvm" FSTYPE="" MOUNTPOINT=""
KNAME="dm-9" PKNAME="dm-8" NAME="vg-lv_thinpool" LABEL="" TYPE="lvm" FSTYPE="" MOUNTPOINT=""
KNAME="dm-10" PKNAME="dm-8" NAME="vg-lv_root" LABEL="img-rootfs" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/"
KNAME="dm-11" PKNAME="dm-8" NAME="vg-lv_tmp" LABEL="fs_tmp" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/tmp"
KNAME="dm-12" PKNAME="dm-8" NAME="vg-lv_var" LABEL="fs_var" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/var"
KNAME="dm-13" PKNAME="dm-8" NAME="vg-lv_log" LABEL="fs_log" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/var/log"
KNAME="dm-14" PKNAME="dm-8" NAME="vg-lv_audit" LABEL="fs_audit" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/var/log/audit"
KNAME="dm-15" PKNAME="dm-8" NAME="vg-lv_home" LABEL="fs_home" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/home"
KNAME="dm-16" PKNAME="dm-8" NAME="vg-lv_srv" LABEL="fs_srv" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/srv"
KNAME="dm-7" PKNAME="dm-4" NAME="vg-lv_thinpool_tdata" LABEL="" TYPE="lvm" FSTYPE="" MOUNTPOINT=""
KNAME="dm-8" PKNAME="dm-7" NAME="vg-lv_thinpool-tpool" LABEL="" TYPE="lvm" FSTYPE="" MOUNTPOINT=""
KNAME="dm-9" PKNAME="dm-8" NAME="vg-lv_thinpool" LABEL="" TYPE="lvm" FSTYPE="" MOUNTPOINT=""
KNAME="dm-10" PKNAME="dm-8" NAME="vg-lv_root" LABEL="img-rootfs" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/"
KNAME="dm-11" PKNAME="dm-8" NAME="vg-lv_tmp" LABEL="fs_tmp" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/tmp"
KNAME="dm-12" PKNAME="dm-8" NAME="vg-lv_var" LABEL="fs_var" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/var"
KNAME="dm-13" PKNAME="dm-8" NAME="vg-lv_log" LABEL="fs_log" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/var/log"
KNAME="dm-14" PKNAME="dm-8" NAME="vg-lv_audit" LABEL="fs_audit" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/var/log/audit"
KNAME="dm-15" PKNAME="dm-8" NAME="vg-lv_home" LABEL="fs_home" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/home"
KNAME="dm-16" PKNAME="dm-8" NAME="vg-lv_srv" LABEL="fs_srv" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/srv"
KNAME="dm-5" PKNAME="dm-0" NAME="mpatha5" LABEL="config-2" TYPE="part" FSTYPE="iso9660" MOUNTPOINT=""
KNAME="sdb" PKNAME="" NAME="sdb" LABEL="" TYPE="disk" FSTYPE="mpath_member" MOUNTPOINT=""
KNAME="dm-0" PKNAME="sdb" NAME="mpatha" LABEL="" TYPE="mpath" FSTYPE="" MOUNTPOINT=""
KNAME="dm-1" PKNAME="dm-0" NAME="mpatha1" LABEL="MKFS_ESP" TYPE="part" FSTYPE="vfat" MOUNTPOINT="/boot/efi"
KNAME="dm-2" PKNAME="dm-0" NAME="mpatha2" LABEL="" TYPE="part" FSTYPE="" MOUNTPOINT=""
KNAME="dm-3" PKNAME="dm-0" NAME="mpatha3" LABEL="mkfs_boot" TYPE="part" FSTYPE="ext4" MOUNTPOINT="/boot"
KNAME="dm-4" PKNAME="dm-0" NAME="mpatha4" LABEL="" TYPE="part" FSTYPE="LVM2_member" MOUNTPOINT=""
KNAME="dm-6" PKNAME="dm-4" NAME="vg-lv_thinpool_tmeta" LABEL="" TYPE="lvm" FSTYPE="" MOUNTPOINT=""
KNAME="dm-8" PKNAME="dm-6" NAME="vg-lv_thinpool-tpool" LABEL="" TYPE="lvm" FSTYPE="" MOUNTPOINT=""
KNAME="dm-9" PKNAME="dm-8" NAME="vg-lv_thinpool" LABEL="" TYPE="lvm" FSTYPE="" MOUNTPOINT=""
KNAME="dm-10" PKNAME="dm-8" NAME="vg-lv_root" LABEL="img-rootfs" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/"
KNAME="dm-11" PKNAME="dm-8" NAME="vg-lv_tmp" LABEL="fs_tmp" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/tmp"
KNAME="dm-12" PKNAME="dm-8" NAME="vg-lv_var" LABEL="fs_var" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/var"
KNAME="dm-13" PKNAME="dm-8" NAME="vg-lv_log" LABEL="fs_log" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/var/log"
KNAME="dm-14" PKNAME="dm-8" NAME="vg-lv_audit" LABEL="fs_audit" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/var/log/audit"
KNAME="dm-15" PKNAME="dm-8" NAME="vg-lv_home" LABEL="fs_home" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/home"
KNAME="dm-16" PKNAME="dm-8" NAME="vg-lv_srv" LABEL="fs_srv" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/srv"
KNAME="dm-7" PKNAME="dm-4" NAME="vg-lv_thinpool_tdata" LABEL="" TYPE="lvm" FSTYPE="" MOUNTPOINT=""
KNAME="dm-8" PKNAME="dm-7" NAME="vg-lv_thinpool-tpool" LABEL="" TYPE="lvm" FSTYPE="" MOUNTPOINT=""
KNAME="dm-9" PKNAME="dm-8" NAME="vg-lv_thinpool" LABEL="" TYPE="lvm" FSTYPE="" MOUNTPOINT=""
KNAME="dm-10" PKNAME="dm-8" NAME="vg-lv_root" LABEL="img-rootfs" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/"
KNAME="dm-11" PKNAME="dm-8" NAME="vg-lv_tmp" LABEL="fs_tmp" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/tmp"
KNAME="dm-12" PKNAME="dm-8" NAME="vg-lv_var" LABEL="fs_var" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/var"
KNAME="dm-13" PKNAME="dm-8" NAME="vg-lv_log" LABEL="fs_log" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/var/log"
KNAME="dm-14" PKNAME="dm-8" NAME="vg-lv_audit" LABEL="fs_audit" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/var/log/audit"
KNAME="dm-15" PKNAME="dm-8" NAME="vg-lv_home" LABEL="fs_home" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/home"
KNAME="dm-16" PKNAME="dm-8" NAME="vg-lv_srv" LABEL="fs_srv" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/srv"
KNAME="dm-5" PKNAME="dm-0" NAME="mpatha5" LABEL="config-2" TYPE="part" FSTYPE="iso9660" MOUNTPOINT=""
KNAME="sdc" PKNAME="" NAME="sdc" LABEL="" TYPE="disk" FSTYPE="mpath_member" MOUNTPOINT=""
KNAME="dm-0" PKNAME="sdc" NAME="mpatha" LABEL="" TYPE="mpath" FSTYPE="" MOUNTPOINT=""
KNAME="dm-1" PKNAME="dm-0" NAME="mpatha1" LABEL="MKFS_ESP" TYPE="part" FSTYPE="vfat" MOUNTPOINT="/boot/efi"
KNAME="dm-2" PKNAME="dm-0" NAME="mpatha2" LABEL="" TYPE="part" FSTYPE="" MOUNTPOINT=""
KNAME="dm-3" PKNAME="dm-0" NAME="mpatha3" LABEL="mkfs_boot" TYPE="part" FSTYPE="ext4" MOUNTPOINT="/boot"
KNAME="dm-4" PKNAME="dm-0" NAME="mpatha4" LABEL="" TYPE="part" FSTYPE="LVM2_member" MOUNTPOINT=""
KNAME="dm-6" PKNAME="dm-4" NAME="vg-lv_thinpool_tmeta" LABEL="" TYPE="lvm" FSTYPE="" MOUNTPOINT=""
KNAME="dm-8" PKNAME="dm-6" NAME="vg-lv_thinpool-tpool" LABEL="" TYPE="lvm" FSTYPE="" MOUNTPOINT=""
KNAME="dm-9" PKNAME="dm-8" NAME="vg-lv_thinpool" LABEL="" TYPE="lvm" FSTYPE="" MOUNTPOINT=""
KNAME="dm-10" PKNAME="dm-8" NAME="vg-lv_root" LABEL="img-rootfs" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/"
KNAME="dm-11" PKNAME="dm-8" NAME="vg-lv_tmp" LABEL="fs_tmp" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/tmp"
KNAME="dm-12" PKNAME="dm-8" NAME="vg-lv_var" LABEL="fs_var" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/var"
KNAME="dm-13" PKNAME="dm-8" NAME="vg-lv_log" LABEL="fs_log" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/var/log"
KNAME="dm-14" PKNAME="dm-8" NAME="vg-lv_audit" LABEL="fs_audit" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/var/log/audit"
KNAME="dm-15" PKNAME="dm-8" NAME="vg-lv_home" LABEL="fs_home" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/home"
KNAME="dm-16" PKNAME="dm-8" NAME="vg-lv_srv" LABEL="fs_srv" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/srv"
KNAME="dm-7" PKNAME="dm-4" NAME="vg-lv_thinpool_tdata" LABEL="" TYPE="lvm" FSTYPE="" MOUNTPOINT=""
KNAME="dm-8" PKNAME="dm-7" NAME="vg-lv_thinpool-tpool" LABEL="" TYPE="lvm" FSTYPE="" MOUNTPOINT=""
KNAME="dm-9" PKNAME="dm-8" NAME="vg-lv_thinpool" LABEL="" TYPE="lvm" FSTYPE="" MOUNTPOINT=""
KNAME="dm-10" PKNAME="dm-8" NAME="vg-lv_root" LABEL="img-rootfs" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/"
KNAME="dm-11" PKNAME="dm-8" NAME="vg-lv_tmp" LABEL="fs_tmp" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/tmp"
KNAME="dm-12" PKNAME="dm-8" NAME="vg-lv_var" LABEL="fs_var" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/var"
KNAME="dm-13" PKNAME="dm-8" NAME="vg-lv_log" LABEL="fs_log" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/var/log"
KNAME="dm-14" PKNAME="dm-8" NAME="vg-lv_audit" LABEL="fs_audit" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/var/log/audit"
KNAME="dm-15" PKNAME="dm-8" NAME="vg-lv_home" LABEL="fs_home" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/home"
KNAME="dm-16" PKNAME="dm-8" NAME="vg-lv_srv" LABEL="fs_srv" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/srv"
KNAME="dm-5" PKNAME="dm-0" NAME="mpatha5" LABEL="config-2" TYPE="part" FSTYPE="iso9660" MOUNTPOINT=""
KNAME="sdd" PKNAME="" NAME="sdd" LABEL="" TYPE="disk" FSTYPE="mpath_member" MOUNTPOINT=""
KNAME="dm-0" PKNAME="sdd" NAME="mpatha" LABEL="" TYPE="mpath" FSTYPE="" MOUNTPOINT=""
KNAME="dm-1" PKNAME="dm-0" NAME="mpatha1" LABEL="MKFS_ESP" TYPE="part" FSTYPE="vfat" MOUNTPOINT="/boot/efi"
KNAME="dm-2" PKNAME="dm-0" NAME="mpatha2" LABEL="" TYPE="part" FSTYPE="" MOUNTPOINT=""
KNAME="dm-3" PKNAME="dm-0" NAME="mpatha3" LABEL="mkfs_boot" TYPE="part" FSTYPE="ext4" MOUNTPOINT="/boot"
KNAME="dm-4" PKNAME="dm-0" NAME="mpatha4" LABEL="" TYPE="part" FSTYPE="LVM2_member" MOUNTPOINT=""
KNAME="dm-6" PKNAME="dm-4" NAME="vg-lv_thinpool_tmeta" LABEL="" TYPE="lvm" FSTYPE="" MOUNTPOINT=""
KNAME="dm-8" PKNAME="dm-6" NAME="vg-lv_thinpool-tpool" LABEL="" TYPE="lvm" FSTYPE="" MOUNTPOINT=""
KNAME="dm-9" PKNAME="dm-8" NAME="vg-lv_thinpool" LABEL="" TYPE="lvm" FSTYPE="" MOUNTPOINT=""
KNAME="dm-10" PKNAME="dm-8" NAME="vg-lv_root" LABEL="img-rootfs" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/"
KNAME="dm-11" PKNAME="dm-8" NAME="vg-lv_tmp" LABEL="fs_tmp" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/tmp"
KNAME="dm-12" PKNAME="dm-8" NAME="vg-lv_var" LABEL="fs_var" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/var"
KNAME="dm-13" PKNAME="dm-8" NAME="vg-lv_log" LABEL="fs_log" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/var/log"
KNAME="dm-14" PKNAME="dm-8" NAME="vg-lv_audit" LABEL="fs_audit" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/var/log/audit"
KNAME="dm-15" PKNAME="dm-8" NAME="vg-lv_home" LABEL="fs_home" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/home"
KNAME="dm-16" PKNAME="dm-8" NAME="vg-lv_srv" LABEL="fs_srv" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/srv"
KNAME="dm-7" PKNAME="dm-4" NAME="vg-lv_thinpool_tdata" LABEL="" TYPE="lvm" FSTYPE="" MOUNTPOINT=""
KNAME="dm-8" PKNAME="dm-7" NAME="vg-lv_thinpool-tpool" LABEL="" TYPE="lvm" FSTYPE="" MOUNTPOINT=""
KNAME="dm-9" PKNAME="dm-8" NAME="vg-lv_thinpool" LABEL="" TYPE="lvm" FSTYPE="" MOUNTPOINT=""
KNAME="dm-10" PKNAME="dm-8" NAME="vg-lv_root" LABEL="img-rootfs" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/"
KNAME="dm-11" PKNAME="dm-8" NAME="vg-lv_tmp" LABEL="fs_tmp" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/tmp"
KNAME="dm-12" PKNAME="dm-8" NAME="vg-lv_var" LABEL="fs_var" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/var"
KNAME="dm-13" PKNAME="dm-8" NAME="vg-lv_log" LABEL="fs_log" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/var/log"
KNAME="dm-14" PKNAME="dm-8" NAME="vg-lv_audit" LABEL="fs_audit" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/var/log/audit"
KNAME="dm-15" PKNAME="dm-8" NAME="vg-lv_home" LABEL="fs_home" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/home"
KNAME="dm-16" PKNAME="dm-8" NAME="vg-lv_srv" LABEL="fs_srv" TYPE="lvm" FSTYPE="xfs" MOUNTPOINT="/srv"
KNAME="dm-5" PKNAME="dm-0" NAME="mpatha5" LABEL="config-2" TYPE="part" FSTYPE="iso9660" MOUNTPOINT=""
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
SGDISK_V = """
Problem: The secondary header's self-pointer indicates that it doesn't reside
at the end of the disk. If you've added a disk to a RAID array, use the 'e'
option on the experts' menu to adjust the secondary header's and partition
table's locations.

Identified 1 problems!"""

# output of vgs --noheadings --options vg_name
VGS = "  vg\n"

# output of lvs --noheadings --options lv_name,lv_dm_path,lv_attr,pool_lv
LVS = '''
  lv_audit    /dev/mapper/vg-lv_audit    Vwi-aotz--
  lv_home     /dev/mapper/vg-lv_home     Vwi-aotz--
  lv_log      /dev/mapper/vg-lv_log      Vwi-aotz--
  lv_root     /dev/mapper/vg-lv_root     Vwi-aotz--
  lv_srv      /dev/mapper/vg-lv_srv      Vwi-aotz--
  lv_tmp      /dev/mapper/vg-lv_tmp      Vwi-aotz--
  lv_var      /dev/mapper/vg-lv_var      Vwi-aotz--
'''

LVS_THIN = '''
  lv_audit    /dev/mapper/vg-lv_audit    Vwi-aotz-- lv_thinpool
  lv_home     /dev/mapper/vg-lv_home     Vwi-aotz-- lv_thinpool
  lv_log      /dev/mapper/vg-lv_log      Vwi-aotz-- lv_thinpool
  lv_root     /dev/mapper/vg-lv_root     Vwi-aotz-- lv_thinpool
  lv_srv      /dev/mapper/vg-lv_srv      Vwi-aotz-- lv_thinpool
  lv_thinpool /dev/mapper/vg-lv_thinpool twi-aotz--
  lv_tmp      /dev/mapper/vg-lv_tmp      Vwi-aotz-- lv_thinpool
  lv_var      /dev/mapper/vg-lv_var      Vwi-aotz-- lv_thinpool
'''


class TestGrowvols(base.BaseTestCase):

    def test_printable_cmd(self):
        self.assertEqual(
            "foo --thing 'bar baz'",
            growvols.printable_cmd(['foo', '--thing', "bar baz"])
        )

    def test_convert_bytes(self):
        self.assertEqual('100B', growvols.convert_bytes(100))
        self.assertEqual('1000B', growvols.convert_bytes(1000))
        self.assertEqual('1MiB', growvols.convert_bytes(2000000))
        self.assertEqual('2GiB', growvols.convert_bytes(3000000000))
        self.assertEqual('3725GiB', growvols.convert_bytes(4000000000000))

    def test_shrink_bytes_for_alignment(self):
        peb = growvols.PHYSICAL_EXTENT_BYTES
        half_peb = peb // 2

        # shrink 3 extents to 1
        self.assertEqual(peb, growvols.shrink_bytes_for_alignment(peb * 3))

        # shrink 4.5 extents to 2 (round down to whole extent minus 2 extents)
        self.assertEqual(peb * 2,
                         growvols.shrink_bytes_for_alignment(
                             peb * 4 + half_peb))

        # error shrinking zero
        e = self.assertRaises(Exception,
                              growvols.shrink_bytes_for_alignment, 0)
        self.assertIn('Requires more than 8MiB, requested: 0B', str(e))

        # error shrinking 1 extent
        e = self.assertRaises(Exception,
                              growvols.shrink_bytes_for_alignment, peb)
        self.assertIn('Requires more than 8MiB, requested: 4MiB', str(e))

        # error shrinking 2 extents
        e = self.assertRaises(Exception,
                              growvols.shrink_bytes_for_alignment, peb * 2)
        self.assertIn('Requires more than 8MiB, requested: 8MiB', str(e))

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

    def test_parse_shell_vars_multipath(self):
        devices = list(growvols.parse_shell_vars(LSBLK_MULTIPATH))
        self.assertEqual(108, len(devices))

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

    def test_find_device_multipath(self):
        mpatha = {
            'FSTYPE': '',
            'KNAME': 'dm-0',
            'LABEL': '',
            'MOUNTPOINT': '',
            'NAME': 'mpatha',
            'PKNAME': 'sda',
            'TYPE': 'mpath'
        }
        devices = list(growvols.parse_shell_vars(LSBLK_MULTIPATH))
        self.assertEqual(
            mpatha,
            growvols.find_device(
                devices, ['KNAME', 'NAME'], 'mpatha'))

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
        self.assertEqual('Expected a device with TYPE="disk" or TYPE="mpath"'
                         ', got: dissed',
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
        opts = mock.Mock()
        opts.device = None
        disk = growvols.find_disk(opts, DEVICES)
        self.assertEqual(5, growvols.find_next_partnum(DEVICES, disk))
        disk = {
            "FSTYPE": "",
            "KNAME": "sdb",
            "LABEL": "",
            "MOUNTPOINT": "",
            "NAME": "sdb",
            "PKNAME": "",
            "TYPE": "disk",
        }
        self.assertEqual(1, growvols.find_next_partnum(DEVICES, disk))

    def test_find_next_partnum_multipath(self):
        opts = mock.Mock()
        opts.device = 'mpatha'
        devices = list(growvols.parse_shell_vars(LSBLK_MULTIPATH))
        disk = growvols.find_disk(opts, devices)
        self.assertEqual(6, growvols.find_next_partnum(devices, disk))

    def test_find_next_partnum_multipath_partition_delimiter(self):
        opts = mock.Mock()
        opts.device = 'mpath2'
        local_lsblk = copy.deepcopy(LSBLK_MULTIPATH)
        local_lsblk = local_lsblk.replace('mpatha1', 'mpath2p1')
        local_lsblk = local_lsblk.replace('mpatha2', 'mpath2p2')
        local_lsblk = local_lsblk.replace('mpatha3', 'mpath2p3')
        local_lsblk = local_lsblk.replace('mpatha4', 'mpath2p4')
        local_lsblk = local_lsblk.replace('mpatha', 'mpath2')
        devices = list(growvols.parse_shell_vars(local_lsblk))
        disk = growvols.find_disk(opts, devices)
        self.assertEqual(6, growvols.find_next_partnum(devices, disk))

    def test_find_next_device_name(self):
        devices = list(growvols.parse_shell_vars(LSBLK))
        disk = {
            "FSTYPE": "",
            "KNAME": "sda",
            "LABEL": "",
            "MOUNTPOINT": "",
            "NAME": "sda",
            "PKNAME": "",
            "TYPE": "disk",
        }
        # Use SATA etc device naming
        self.assertEqual(
            'sda5',
            growvols.find_next_device_name(devices, disk, 5))

    def test_find_next_device_name_no_partitions(self):
        devices = list(growvols.parse_shell_vars(LSBLK))
        disk_no_partitions = {
            "FSTYPE": "",
            "KNAME": "sdb",
            "LABEL": "",
            "MOUNTPOINT": "",
            "NAME": "sdb",
            "PKNAME": "",
            "TYPE": "disk",
        }
        # No partitions
        e = self.assertRaises(Exception, growvols.find_next_device_name,
                              devices, disk_no_partitions, 1)
        self.assertEqual(
            'Could not find partition naming scheme for sdb', str(e))

    def test_find_next_device_name_nvme(self):
        devices = list(growvols.parse_shell_vars(LSBLK))
        disk = {
            "FSTYPE": "",
            "KNAME": "nvme0",
            "LABEL": "",
            "MOUNTPOINT": "",
            "NAME": "nvme0",
            "PKNAME": "",
            "TYPE": "disk",
        }
        # Use NVMe device naming
        for i in (1, 2, 3, 4):
            d = growvols.find_device(devices, 'KNAME', 'sda%s' % i)
            d['KNAME'] = 'nvme0p%s' % i
            d['NAME'] = 'nvme0p%s' % i
        self.assertEqual(
            'nvme0p5',
            growvols.find_next_device_name(devices, disk, 5))

    def test_find_next_device_name_multipath(self):
        opts = mock.Mock()
        opts.device = 'mpatha'
        devices = list(growvols.parse_shell_vars(LSBLK_MULTIPATH))
        disk = growvols.find_disk(opts, devices)

        # Use dm device naming
        self.assertEqual(
            'mpatha6',
            growvols.find_next_device_name(devices, disk, 6))

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
            {'/dev/mapper/vg-lv_root': fidy_g},
            growvols.find_grow_vols(opts, DEVICES, 'vg', fidy_g)
        )

        # assign to /home, /var, remainder to /
        opts.grow_vols = ['/home=20%', 'fs_var=40%']
        self.assertEqual(
            {
                '/dev/mapper/vg-lv_home': ten_g,
                '/dev/mapper/vg-lv_var': ten_g * 2,
                '/dev/mapper/vg-lv_root': ten_g * 2
            },
            growvols.find_grow_vols(opts, DEVICES, 'vg', fidy_g)
        )

        # assign to /home, /var, /tmp by amount
        opts.grow_vols = ['/home=19GiB', 'fs_var=30GiB', '/tmp=1GiB']
        self.assertEqual(
            {
                '/dev/mapper/vg-lv_home': one_g * 19,
                '/dev/mapper/vg-lv_var': one_g * 30,
                '/dev/mapper/vg-lv_tmp': one_g
            },
            growvols.find_grow_vols(opts, DEVICES, 'vg', fidy_g)
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

    @mock.patch('growvols.execute')
    def test_find_thin_pool(self, mock_execute):
        self._find_thin_pool(mock_execute, DEVICES)

    @mock.patch('growvols.execute')
    def test_find_thin_pool_multipath(self, mock_execute):
        devices = list(growvols.parse_shell_vars(LSBLK_MULTIPATH))
        self._find_thin_pool(mock_execute, devices)

    def _find_thin_pool(self, mock_execute, devices):
        # No thin pool
        mock_execute.return_value = LVS
        self.assertEqual((None, None), growvols.find_thin_pool(devices, 'vg'))
        mock_execute.assert_called_once_with([
            'lvs', '--noheadings', '--options',
            'lv_name,lv_dm_path,lv_attr,pool_lv'])

        # One thin pool, all volumes use it
        mock_execute.return_value = LVS_THIN
        self.assertEqual(('/dev/mapper/vg-lv_thinpool', 'lv_thinpool'),
                         growvols.find_thin_pool(devices, 'vg'))

        # One pool, not used by all volumes
        mock_execute.return_value = '''
  lv_thinpool /dev/mapper/vg-lv_thinpool twi-aotz--
  lv_home     /dev/mapper/vg-lv_home     Vwi-aotz--
  lv_root     /dev/mapper/vg-lv_root     Vwi-aotz-- lv_thinpool'''
        e = self.assertRaises(Exception, growvols.find_thin_pool,
                              devices, 'vg')
        self.assertEqual('All volumes need to be in pool lv_thinpool. '
                         'lv_home is in pool None', str(e))

        # Two pools, volumes use both
        mock_execute.return_value = '''
  lv_thin1 /dev/mapper/vg-lv_thin1 twi-aotz--
  lv_thin2 /dev/mapper/vg-lv_thin2 twi-aotz--
  lv_home  /dev/mapper/vg-lv_home  Vwi-aotz-- lv_thin2
  lv_root  /dev/mapper/vg-lv_root  Vwi-aotz-- lv_thin1'''
        e = self.assertRaises(Exception, growvols.find_thin_pool,
                              devices, 'vg')
        self.assertEqual('All volumes need to be in pool lv_thin1. '
                         'lv_home is in pool lv_thin2', str(e))

    @mock.patch('growvols.find_sector_size')
    @mock.patch('growvols.execute')
    def test_main(self, mock_execute, mock_sector_size):
        mock_sector_size.return_value = 512

        # noop, only discover block device info
        mock_execute.side_effect = [
            LSBLK,
            SGDISK_V,
            '',
            '',
            SGDISK_LARGEST,
            VGS,
            LVS,
        ]
        growvols.main(['growvols', '--noop'])
        mock_execute.assert_has_calls([
            mock.call(['lsblk', '-Po',
                       'kname,pkname,name,label,type,fstype,mountpoint']),
            mock.call(['sgdisk', '-v', '/dev/sda']),
            mock.call(['sgdisk', '-e', '/dev/sda']),
            mock.call(['partprobe']),
            mock.call(['sgdisk', '--first-aligned-in-largest',
                       '--end-of-largest', '/dev/sda']),
            mock.call(['vgs', '--noheadings', '--options', 'vg_name']),
            mock.call(['lvs', '--noheadings', '--options',
                       'lv_name,lv_dm_path,lv_attr,pool_lv'])
        ])

        # no arguments, assign all to /
        mock_execute.reset_mock()
        mock_execute.side_effect = [
            LSBLK,
            '',
            SGDISK_LARGEST,
            VGS,
            LVS,
            '', '', '', '', '', ''
        ]
        growvols.main(['growvols', '--yes'])
        mock_execute.assert_has_calls([
            mock.call(['lsblk', '-Po',
                       'kname,pkname,name,label,type,fstype,mountpoint']),
            mock.call(['sgdisk', '-v', '/dev/sda']),
            mock.call(['sgdisk', '--first-aligned-in-largest',
                       '--end-of-largest', '/dev/sda']),
            mock.call(['vgs', '--noheadings', '--options', 'vg_name']),
            mock.call(['lvs', '--noheadings', '--options',
                       'lv_name,lv_dm_path,lv_attr,pool_lv']),
            mock.call(['sgdisk', '--new=5:79267840:488265727',
                       '--change-name=5:growvols', '/dev/sda']),
            mock.call(['partprobe']),
            mock.call(['pvcreate', '-ff', '--yes', '/dev/sda5']),
            mock.call(['vgextend', 'vg', '/dev/sda5']),
            mock.call(['lvextend', '--size', '+209396432896B',
                       '/dev/mapper/vg-lv_root', '/dev/sda5']),
            mock.call(['xfs_growfs', '/dev/mapper/vg-lv_root'])
        ])

        # assign to /home, /var, remainder to /
        mock_execute.reset_mock()
        mock_execute.side_effect = [
            LSBLK,
            '',
            SGDISK_LARGEST,
            VGS,
            LVS,
            '', '', '', '', '', '', '', '', '', ''
        ]
        growvols.main(['growvols', '--yes', '--group', 'vg',
                       '/home=20%', 'fs_var=40%'])
        mock_execute.assert_has_calls([
            mock.call(['lsblk', '-Po',
                       'kname,pkname,name,label,type,fstype,mountpoint']),
            mock.call(['sgdisk', '-v', '/dev/sda']),
            mock.call(['sgdisk', '--first-aligned-in-largest',
                       '--end-of-largest', '/dev/sda']),
            mock.call(['vgs', '--noheadings', '--options', 'vg_name']),
            mock.call(['lvs', '--noheadings', '--options',
                       'lv_name,lv_dm_path,lv_attr,pool_lv']),
            mock.call(['sgdisk', '--new=5:79267840:488265727',
                       '--change-name=5:growvols', '/dev/sda']),
            mock.call(['partprobe']),
            mock.call(['pvcreate', '-ff', '--yes', '/dev/sda5']),
            mock.call(['vgextend', 'vg', '/dev/sda5']),
            mock.call(['lvextend', '--size', '+41871736832B',
                       '/dev/mapper/vg-lv_home', '/dev/sda5']),
            mock.call(['lvextend', '--size', '+83751862272B',
                       '/dev/mapper/vg-lv_var', '/dev/sda5']),
            mock.call(['lvextend', '--size', '+83756056576B',
                       '/dev/mapper/vg-lv_root', '/dev/sda5']),
            mock.call(['xfs_growfs', '/dev/mapper/vg-lv_home']),
            mock.call(['xfs_growfs', '/dev/mapper/vg-lv_var']),
            mock.call(['xfs_growfs', '/dev/mapper/vg-lv_root']),
        ])

        # no space to grow, failed
        sector_start = 79267840
        sector_end = sector_start + 1024
        sgdisk_largest = "%s\n%s\n" % (sector_start, sector_end)
        mock_execute.side_effect = [
            LSBLK,
            '',
            sgdisk_largest,
            VGS,
            LVS,
        ]
        self.assertEqual(
            2,
            growvols.main(['growvols', '--exit-on-no-grow'])
        )

        # no space to grow, success
        mock_execute.side_effect = [
            LSBLK,
            '',
            sgdisk_largest,
            VGS,
            LVS,
        ]
        self.assertEqual(
            0,
            growvols.main(['growvols'])
        )

    @mock.patch('growvols.find_sector_size')
    @mock.patch('growvols.execute')
    def test_main_thin_provision(self, mock_execute, mock_sector_size):
        mock_sector_size.return_value = 512

        # assign to /home, /var, remainder to /
        mock_execute.reset_mock()
        mock_execute.side_effect = [
            LSBLK,
            '',
            SGDISK_LARGEST,
            VGS,
            LVS_THIN,
            '', '', '', '', '', '', '', '', '', '', '', ''
        ]
        growvols.main(['growvols', '--yes', '--group', 'vg',
                       '/home=20%', 'fs_var=40%'])
        mock_execute.assert_has_calls([
            mock.call(['lsblk', '-Po',
                       'kname,pkname,name,label,type,fstype,mountpoint']),
            mock.call(['sgdisk', '-v', '/dev/sda']),
            mock.call(['sgdisk', '--first-aligned-in-largest',
                       '--end-of-largest', '/dev/sda']),
            mock.call(['vgs', '--noheadings', '--options', 'vg_name']),
            mock.call(['lvs', '--noheadings', '--options',
                       'lv_name,lv_dm_path,lv_attr,pool_lv']),
            mock.call(['sgdisk', '--new=5:79267840:488265727',
                       '--change-name=5:growvols', '/dev/sda']),
            mock.call(['partprobe']),
            mock.call(['pvcreate', '-ff', '--yes', '/dev/sda5']),
            mock.call(['vgextend', 'vg', '/dev/sda5']),
            mock.call(['lvextend', '--poolmetadatasize', '+1073741824B',
                       'vg/lv_thinpool']),
            mock.call(['lvextend', '-L+207244754944B',
                       '/dev/mapper/vg-lv_thinpool', '/dev/sda5']),
            mock.call(['lvextend', '--size', '+41439723520B',
                       '/dev/mapper/vg-lv_home']),
            mock.call(['lvextend', '--size', '+82892029952B',
                       '/dev/mapper/vg-lv_var']),
            mock.call(['lvextend', '--size', '+82896224256B',
                       '/dev/mapper/vg-lv_root']),
            mock.call(['xfs_growfs', '/dev/mapper/vg-lv_home']),
            mock.call(['xfs_growfs', '/dev/mapper/vg-lv_var']),
            mock.call(['xfs_growfs', '/dev/mapper/vg-lv_root']),
        ])

    @mock.patch('growvols.find_sector_size')
    @mock.patch('growvols.execute')
    def test_main_thin_provision_multipath(self, mock_execute,
                                           mock_sector_size):
        mock_sector_size.return_value = 512

        # assign to /home, /var, remainder to /
        mock_execute.reset_mock()
        mock_execute.side_effect = [
            LSBLK_MULTIPATH,
            '',
            SGDISK_LARGEST,
            VGS,
            LVS_THIN,
            '', '', '', '', '', '', '', '', '', '', '', '', ''
        ]
        growvols.main(['growvols', '--yes', '--device', 'mpatha',
                       '--group', 'vg',
                       '/home=20%', 'fs_var=40%'])
        mock_execute.assert_has_calls([
            mock.call(['lsblk', '-Po',
                       'kname,pkname,name,label,type,fstype,mountpoint']),
            mock.call(['sgdisk', '-v', '/dev/dm-0']),
            mock.call(['sgdisk', '--first-aligned-in-largest',
                       '--end-of-largest', '/dev/dm-0']),
            mock.call(['vgs', '--noheadings', '--options', 'vg_name']),
            mock.call(['lvs', '--noheadings', '--options',
                       'lv_name,lv_dm_path,lv_attr,pool_lv']),
            mock.call(['sgdisk', '--new=6:79267840:488265727',
                       '--change-name=6:growvols', '/dev/dm-0']),
            mock.call(['multipath', '-r']),
            mock.call(['partprobe']),
            mock.call(['pvcreate', '-ff', '--yes', '/dev/mapper/mpatha6']),
            mock.call(['vgextend', 'vg', '/dev/mapper/mpatha6']),
            mock.call(['lvextend', '--poolmetadatasize', '+1073741824B',
                       'vg/lv_thinpool']),
            mock.call(['lvextend', '-L+207244754944B',
                       '/dev/mapper/vg-lv_thinpool', '/dev/mapper/mpatha6']),
            mock.call(['lvextend', '--size', '+41439723520B',
                       '/dev/mapper/vg-lv_home']),
            mock.call(['lvextend', '--size', '+82892029952B',
                       '/dev/mapper/vg-lv_var']),
            mock.call(['lvextend', '--size', '+82896224256B',
                       '/dev/mapper/vg-lv_root']),
            mock.call(['xfs_growfs', '/dev/mapper/vg-lv_home']),
            mock.call(['xfs_growfs', '/dev/mapper/vg-lv_var']),
            mock.call(['xfs_growfs', '/dev/mapper/vg-lv_root']),
        ])
