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

import codecs
from diskimage_builder.block_device.blockdevicesetupexception \
    import BlockDeviceSetupException
from diskimage_builder.block_device.level0 import LocalLoop
from diskimage_builder.block_device.level1 import Partitioning
from diskimage_builder.graph.digraph import Digraph
import json
import logging
import os
import shutil
import sys
import yaml


logger = logging.getLogger(__name__)


class BlockDevice(object):

    # Default configuration:
    # one image, one partition, mounted under '/'
    DefaultConfig = """
local_loop:
  name: image0
"""

# This is an example of the next level config
# mkfs:
#  base: root_p1
#  type: ext4
#  mount_point: /

    # A dictionary to map sensible names to internal implementation.
    cfg_type_map = {
        'local_loop': LocalLoop,
        'partitioning': Partitioning,
        'mkfs': 'not yet implemented',
    }

    def __init__(self, block_device_config, build_dir,
                 default_image_size, default_image_dir):
        logger.debug("Creating BlockDevice object")
        logger.debug("Config given [%s]" % block_device_config)
        logger.debug("Build dir [%s]" % build_dir)
        if block_device_config is None:
            block_device_config = BlockDevice.DefaultConfig
        self.config = yaml.safe_load(block_device_config)
        logger.debug("Using config [%s]" % self.config)

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
        with codecs.open(self.state_json_file_name,
                         encoding="utf-8", mode="r") as fd:
            return json.load(fd)

    def create_graph(self, config, default_config):
        # This is the directed graph of nodes: each parse method must
        # add the appropriate nodes and edges.
        dg = Digraph()

        for cfg_obj_name, cfg_obj_val in config.items():
            # As the first step the configured objects are created
            # (if it exists)
            if cfg_obj_name not in BlockDevice.cfg_type_map:
                logger.error("Configured top level element [%s] "
                             "does not exists." % cfg_obj_name)
                return 1
            cfg_obj = BlockDevice.cfg_type_map[cfg_obj_name](
                cfg_obj_val, default_config)
            # At this point it is only possible to add the nodes:
            # adding the edges needs all nodes first.
            cfg_obj.insert_nodes(dg)

        # Now that all the nodes exists: add also the edges
        for node in dg.get_iter_nodes_values():
            node.insert_edges(dg)

        call_order = dg.topological_sort()
        logger.debug("Call order [%s]" % (list(call_order)))
        return dg, call_order

    def create(self, result, rollback):
        dg, call_order = self.create_graph(self.config, self.default_config)
        for node in call_order:
            node.create(result, rollback)

    def cmd_create(self):
        """Creates the block device"""

        logger.info("create() called")
        logger.debug("Using config [%s]" % self.config)

        result = {}
        rollback = []

        try:
            self.create(result, rollback)
        except BlockDeviceSetupException as bdse:
            logger.error("exception [%s]" % bdse)
            for rollback_cb in reversed(rollback):
                rollback_cb()
            sys.exit(1)

        # To be compatible with the current implementation, echo the
        # result to stdout.
        # If there is no partition needed, pass back directly the
        # image.
        if 'root_p1' in result:
            print("%s" % result['root_p1']['device'])
        else:
            print("%s" % result['image0']['device'])

        self.write_state(result)

        logger.info("create() finished")
        return 0

    def _load_state(self):
        logger.info("_load_state() called")
        try:
            os.stat(self.state_json_file_name)
        except OSError:
            logger.info("State already cleaned - no way to do anything here")
            return None, None, None

        config, default_config, state = self.load_state()
        logger.debug("Using config [%s]" % config)
        logger.debug("Using default config [%s]" % default_config)
        logger.debug("Using state [%s]" % state)

        # Deleting must be done in reverse order
        dg, call_order = self.create_graph(config, default_config)
        reverse_order = reversed(call_order)
        return dg, reverse_order, state

    def cmd_umount(self):
        """Unmounts the blockdevice and cleanup resources"""

        dg, reverse_order, state = self._load_state()
        if dg is None:
            return 0
        for node in reverse_order:
            node.umount(state)

        # To be compatible with the current implementation, echo the
        # result to stdout.
        print("%s" % state['image0']['image'])

        return 0

    def cmd_cleanup(self):
        """Cleanup all remaining relicts - in good case"""

        dg, reverse_order, state = self._load_state()
        if dg is None:
            return 0
        for node in reverse_order:
            node.cleanup(state)

        logger.info("Removing temporary dir [%s]" % self.state_dir)
        shutil.rmtree(self.state_dir)

        return 0

    def cmd_delete(self):
        """Cleanup all remaining relicts - in case of an error"""

        dg, reverse_order, state = self._load_state()
        if dg is None:
            return 0
        for node in reverse_order:
            node.delete(state)

        logger.info("Removing temporary dir [%s]" % self.state_dir)
        shutil.rmtree(self.state_dir)

        return 0
