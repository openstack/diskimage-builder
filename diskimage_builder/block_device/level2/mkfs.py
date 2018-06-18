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

from diskimage_builder.block_device.exception \
    import BlockDeviceSetupException
from diskimage_builder.block_device.plugin import NodeBase
from diskimage_builder.block_device.plugin import PluginBase
from diskimage_builder.block_device.utils import exec_sudo


logger = logging.getLogger(__name__)


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


class FilesystemNode(NodeBase):

    def __init__(self, config, state):
        logger.debug("Create filesystem object; config [%s]", config)
        super(FilesystemNode, self).__init__(config['name'], state)

        # Parameter check (mandatory)
        for pname in ['base', 'type']:
            if pname not in config:
                raise BlockDeviceSetupException(
                    "Mkfs config needs [%s]" % pname)
            setattr(self, pname, config[pname])

        # Parameter check (optional)
        for pname in ['label', 'opts', 'uuid']:
            setattr(self, pname,
                    config[pname] if pname in config else None)

        if self.label is None:
            self.label = self.name

        # for fat/vfat, we use the label as an identifier for the disk
        # so we need that the label is converted to upper case
        if self.type in ('vfat', 'fat'):
            self.label = self.label.upper()

        # ensure we don't already have a fs with this label ... they
        # all must be unique.
        if 'fs_labels' in self.state:
            if self.label in self.state['fs_labels']:
                raise BlockDeviceSetupException(
                    "File system label [%s] used more than once" % self.label)
            self.state['fs_labels'].append(self.label)
        else:
            self.state['fs_labels'] = [self.label]

        if self.type in file_system_max_label_length:
            if file_system_max_label_length[self.type] < len(self.label):
                raise BlockDeviceSetupException(
                    "Label [{label}] too long for filesystem [{type}]: "
                    "{len} > {max_len}".format(**{
                        'label': self.label,
                        'type': self.type,
                        'len': len(self.label),
                        'max_len': file_system_max_label_length[self.type]}))
        else:
            logger.warning("Length of label [%s] cannot be checked for "
                           "filesystem [%s]: unknown max length",
                           self.label, self.type)
            logger.warning("Continue - but this might lead to an error")

        if self.opts is not None:
            self.opts = self.opts.strip().split(' ')

        if self.uuid is None:
            self.uuid = str(uuid.uuid4())

        logger.debug("Filesystem created [%s]", self)

    def get_edges(self):
        edge_from = [self.base]
        edge_to = []
        return (edge_from, edge_to)

    def create(self):
        cmd = ["mkfs"]

        cmd.extend(['-t', self.type])
        if self.opts:
            cmd.extend(self.opts)

        if self.type in ('vfat', 'fat'):
            cmd.extend(["-n", self.label])
        else:
            cmd.extend(["-L", self.label])

        if self.type in ('ext2', 'ext3', 'ext4'):
            cmd.extend(['-U', self.uuid])
        elif self.type == 'xfs':
            cmd.extend(['-m', "uuid=%s" % self.uuid])
        else:
            logger.warning("UUID will not be written for fs type [%s]",
                           self.type)

        if self.type in ('ext2', 'ext3', 'ext4', 'xfs'):
            cmd.append('-q')

        if 'blockdev' not in self.state:
            self.state['blockdev'] = {}
        device = self.state['blockdev'][self.base]['device']
        cmd.append(device)

        logger.debug("Creating fs command [%s]", cmd)
        exec_sudo(cmd)

        if 'filesys' not in self.state:
            self.state['filesys'] = {}
        self.state['filesys'][self.name] \
            = {'uuid': self.uuid, 'label': self.label,
               'fstype': self.type, 'opts': self.opts,
               'device': device}


class Mkfs(PluginBase):
    """Create a file system

    This block device module handles creating different file
    systems.
    """

    def __init__(self, config, defaults, state):
        super(Mkfs, self).__init__()
        self.filesystems = {}
        fs = FilesystemNode(config, state)
        self.filesystems[fs.get_name()] = fs

    def get_nodes(self):
        nodes = []
        for _, fs in self.filesystems.items():
            nodes.append(fs)
        return nodes
