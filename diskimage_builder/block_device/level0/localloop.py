# Copyright 2016 Andreas Florath (andreas@florath.net)
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
import os

from diskimage_builder.block_device.exception import \
    BlockDeviceSetupException
from diskimage_builder.block_device.plugin import NodeBase
from diskimage_builder.block_device.plugin import PluginBase
from diskimage_builder.block_device.utils import exec_sudo
from diskimage_builder.block_device.utils import parse_abs_size_spec


logger = logging.getLogger(__name__)


def image_create(filename, size):
    logger.info("Create image file [%s]", filename)
    with open(filename, "w") as fd:
        fd.seek(size - 1)
        fd.write("\0")


def image_delete(filename):
    logger.info("Remove image file [%s]", filename)
    os.remove(filename)


def loopdev_attach(filename):
    logger.info("loopdev attach")
    logger.debug("Calling [sudo losetup --show -f %s]", filename)
    block_device = exec_sudo(["losetup", "--show", "-f", filename])
    # [:-1]: Cut of the newline
    block_device = block_device[:-1]
    logger.info("New block device [%s]", block_device)
    return block_device


def loopdev_detach(loopdev):
    logger.info("loopdev detach")
    # loopback dev may be tied up a bit by udev events triggered
    # by partition events
    for try_cnt in range(10, 1, -1):
        try:
            exec_sudo(["losetup", "-d", loopdev])
            return
        except BlockDeviceSetupException as e:
            # Do not raise an error - maybe other cleanup methods
            # can at least do some more work.
            logger.error("loopdev detach failed (%s)", e.returncode)

    logger.debug("Gave up trying to detach [%s]", loopdev)
    return 1


class LocalLoopNode(NodeBase):
    """Level0: Local loop image device handling.

    This class handles local loop devices that can be used
    for VM image installation.
    """
    def __init__(self, config, default_config, state):
        logger.debug("Creating LocalLoop object; config [%s] "
                     "default_config [%s]", config, default_config)
        super(LocalLoopNode, self).__init__(config['name'], state)
        if 'size' in config:
            self.size = parse_abs_size_spec(config['size'])
            logger.debug("Image size [%s]", self.size)
        else:
            self.size = parse_abs_size_spec(default_config['image-size'])
            logger.debug("Using default image size [%s]", self.size)
        if 'directory' in config:
            self.image_dir = config['directory']
        else:
            self.image_dir = default_config['image-dir']
        self.filename = os.path.join(self.image_dir, self.name + ".raw")

    def get_edges(self):
        """Because this is created without base, there are no edges."""
        return ([], [])

    def create(self):
        logger.debug("[%s] Creating loop on [%s] with size [%d]",
                     self.name, self.filename, self.size)

        self.add_rollback(image_delete, self.filename)
        image_create(self.filename, self.size)

        block_device = loopdev_attach(self.filename)
        self.add_rollback(loopdev_detach, block_device)

        if 'blockdev' not in self.state:
            self.state['blockdev'] = {}

        self.state['blockdev'][self.name] = {"device": block_device,
                                             "image": self.filename}
        logger.debug("Created loop  name [%s] device [%s] image [%s]",
                     self.name, block_device, self.filename)
        return

    def umount(self):
        loopdev_detach(self.state['blockdev'][self.name]['device'])

    def delete(self):
        image_delete(self.state['blockdev'][self.name]['image'])


class LocalLoop(PluginBase):

    def __init__(self, config, defaults, state):
        super(LocalLoop, self).__init__()
        self.node = LocalLoopNode(config, defaults, state)

    def get_nodes(self):
        return [self.node]
