# Copyright 2017 Andreas Florath (andreas@florath.net)
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
import uuid

from diskimage_builder.block_device.blockdevice \
    import BlockDeviceSetupException
from diskimage_builder.block_device.tree_config import TreeConfig
from diskimage_builder.block_device.utils import exec_sudo
from diskimage_builder.graph.digraph import Digraph


logger = logging.getLogger(__name__)


# There is the need that filesystem labels are unique:
# if not the boot and / or mount (with LABEL=) might fail.
file_system_labels = set()

# There is the need to check the length of the label of
# the filesystem.  The maximum length depends on the used filesystem.
# This map provides information about the maximum label length.
file_system_max_label_length = {
    "ext2": 16,
    "ext3": 16,
    "ext4": 16,
    "xfs": 12,
    "vfat": 11
}


class Filesystem(Digraph.Node):

    def _config_error(self, msg):
        logger.error(msg)
        raise BlockDeviceSetupException(msg)

    def __init__(self, config):
        logger.debug("Create filesystem object; config [%s]" % config)
        # Parameter check (mandatory)
        for pname in ['base', 'name', 'type']:
            if pname not in config:
                self._config_error("Mkfs config needs [%s]" % pname)
            setattr(self, pname, config[pname])

        # Parameter check (optional)
        for pname in ['label', 'opts', 'uuid']:
            setattr(self, pname,
                    config[pname] if pname in config else None)

        if self.label is None:
            self.label = self.name

        # Historic reasons - this will hopefully vanish in one of
        # the next major releases
        if self.label == "cloudimg-rootfs" and self.type == "xfs":
            logger.warning("Default label [cloudimg-rootfs] too long for xfs "
                           "file system - using [img-rootfs] instead")
            self.label = "img-rootfs"

        if self.label in file_system_labels:
            self._config_error(
                "File system label [%s] used more than once" %
                self.label)
        file_system_labels.add(self.label)

        if self.type in file_system_max_label_length:
            if file_system_max_label_length[self.type] < \
               len(self.label):
                self._config_error(
                    "Label [%s] too long for filesystem [%s]: "
                    "maximum length [%d] provided length [%d]" %
                    (self.label, self.type,
                     file_system_max_label_length[self.type],
                     len(self.label)))
        else:
            logger.warning("Length of label [%s] cannot be checked for "
                           "filesystem [%s]: unknown max length" %
                           (self.label, self.type))
            logger.warning("Continue - but this might lead to an error")

        if self.opts is not None:
            self.opts = self.opts.strip().split(' ')

        if self.uuid is None:
            self.uuid = str(uuid.uuid4())

        Digraph.Node.__init__(self, self.name)

        logger.debug("Filesystem created [%s]" % self)

    def __repr__(self):
        return "<Filesystem base [%s] name [%s] type [%s]>" \
            % (self.base, self.name, self.type)

    def insert_edges(self, dg):
        logger.debug("Insert edge [%s]" % self)
        bnode = dg.find(self.base)
        assert bnode is not None
        dg.create_edge(bnode, self)

    def create(self, result, rollback):
        logger.info("create called; result [%s]" % result)

        cmd = ["mkfs"]

        cmd.extend(['-t', self.type])
        if self.opts:
            cmd.extend(self.opts)
        cmd.extend(["-L", self.label])

        if self.type in ('ext2', 'ext3', 'ext4'):
            cmd.extend(['-U', self.uuid])
        elif self.type == 'xfs':
            cmd.extend(['-m', "uuid=%s" % self.uuid])
        else:
            logger.warning("UUID will not be written for fs type [%s]"
                           % self.type)

        if self.type in ('ext2', 'ext3', 'ext4', 'xfs'):
            cmd.append('-q')

        if 'blockdev' not in result:
            result['blockdev'] = {}
        device = result['blockdev'][self.base]['device']
        cmd.append(device)

        logger.debug("Creating fs command [%s]" % (cmd))
        exec_sudo(cmd)

        if 'filesys' not in result:
            result['filesys'] = {}
        result['filesys'][self.name] \
            = {'uuid': self.uuid, 'label': self.label,
               'fstype': self.type, 'opts': self.opts,
               'device': device}

    def umount(self, state):
        """Mkfs does not need any umount."""
        pass

    def cleanup(self, state):
        """Mkfs does not need any cleanup."""
        pass

    def delete(self, state):
        """Mkfs does not need any delete."""
        pass


class Mkfs(object):
    """Module for creating file systems

    This block device module handles creating different file
    systems.
    """

    type_string = "mkfs"
    tree_config = TreeConfig("mkfs")

    def __init__(self, config, default_config):
        logger.debug("Create Mkfs object; config [%s]" % config)
        logger.debug("default_config [%s]" % default_config)
        self.config = config
        self.default_config = default_config
        self.filesystems = {}

        fs = Filesystem(self.config)
        self.filesystems[fs.get_name()] = fs

    def insert_nodes(self, dg):
        for _, fs in self.filesystems.items():
            logger.debug("Insert node [%s]" % fs)
            dg.add_node(fs)
