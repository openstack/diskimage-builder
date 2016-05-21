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

from diskimage_builder.block_device.level0 import Level0
from diskimage_builder.block_device.utils import convert_to_utf8
import json
import logging
import os
import shutil


logger = logging.getLogger(__name__)


class BlockDevice(object):

    # Currently there is only the need for a first element (which must
    # be a list).
    DefaultConfig = [
        [["local_loop",
          {"name": "rootdisk"}]]]
    # The reason for the complex layout is, that for future layers
    # there is a need to add additional lists, like:
    #  DefaultConfig = [
    #      [["local_loop",
    #        {"name": "rootdisk"}]],
    #      [["partitioning",
    #        {"rootdisk": {
    #            "label": "mbr",
    #            "partitions":
    #            [{"name": "rd-partition1",
    #              "flags": ["boot"],
    #              "size": "100%"}]}}]],
    #      [["fs",
    #        {"rd-partition1": {}}]]
    #  ]

    def __init__(self, block_device_config, build_dir,
                 default_image_size, default_image_dir):
        if block_device_config is None:
            self.config = BlockDevice.DefaultConfig
        else:
            self.config = json.loads(block_device_config)
        self.default_config = {
            'image_size': default_image_size,
            'image_dir': default_image_dir}
        self.state_dir = os.path.join(build_dir,
                                      "states/block-device")
        self.state_json_file_name \
            = os.path.join(self.state_dir, "state.json")

    def write_state(self, result):
        logger.debug("Write state [%s]" % self.state_json_file_name)
        os.makedirs(self.state_dir)
        with open(self.state_json_file_name, "w") as fd:
            json.dump([self.config, self.default_config, result], fd)

    def load_state(self):
        with open(self.state_json_file_name, "r") as fd:
            return convert_to_utf8(json.load(fd))

    def cmd_create(self):
        """Creates the block device"""

        logger.info("create() called")
        logger.debug("config [%s]" % self.config)
        lvl0 = Level0(self.config[0], self.default_config, None)
        result = lvl0.create()
        logger.debug("Result level 0 [%s]" % result)

        # To be compatible with the current implementation, echo the
        # result to stdout.
        print("%s" % result['rootdisk']['device'])

        self.write_state(result)

        logger.info("create() finished")
        return 0

    def cmd_umount(self):
        """Unmounts the blockdevice and cleanup resources"""

        logger.info("umount() called")
        try:
            os.stat(self.state_json_file_name)
        except OSError:
            logger.info("State already cleaned - no way to do anything here")
            return 0

        config, default_config, state = self.load_state()
        logger.debug("Using config [%s]" % config)
        logger.debug("Using default config [%s]" % default_config)
        logger.debug("Using state [%s]" % state)

        level0 = Level0(config[0], default_config, state)
        result = level0.delete()

        # If everything finished well, remove the results.
        if result:
            logger.info("Removing temporary dir [%s]" % self.state_dir)
            shutil.rmtree(self.state_dir)

        # To be compatible with the current implementation, echo the
        # result to stdout.
        print("%s" % state['rootdisk']['image'])

        logger.info("umount() finished result [%d]" % result)
        return 0 if result else 1
