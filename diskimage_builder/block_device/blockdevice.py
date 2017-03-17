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
from diskimage_builder.graph.digraph import Digraph
import json
import logging
import os
import shutil
from stevedore import extension
import sys
import yaml


logger = logging.getLogger(__name__)


class BlockDevice(object):
    """Handles block devices.

    This class handles the complete setup and deletion of all aspects
    of the block device level.

    A typical call sequence:

    cmd_create: creates all the different aspects of the block
       device. When this call is successful, the complete block level
       device is set up, filesystems are created and are mounted at
       the correct position.
       After this call it is possible to copy / install all the needed
       files into the appropriate directories.

    cmd_umount: unmount and detaches all directories and used many
       resources. After this call the used (e.g.) images are still
       available for further handling, e.g. converting from raw in
       some other format.

    cmd_cleanup: removes everything that was created with the
       'cmd_create' call, i.e. all images files themselves and
       internal temporary configuration.

    cmd_delete: unmounts and removes everything that was created
       during the 'cmd_create' all.  This call should be used in error
       conditions when there is the need to remove all allocated
       resources immediately and as good as possible.
       From the functional point of view this is mostly the same as a
       call to 'cmd_umount' and 'cmd_cleanup' - but is typically more
       error tolerance.

    In a script this should be called in the following way:

    dib-block-device --phase=create ...
    trap "dib-block-device --phase=delete ..." EXIT
    # copy / install files
    dib-block-device --phase=umount ...
    # convert image(s)
    dib-block-device --phase=cleanup ...
    trap - EXIT
    """

    # Default configuration:
    # one image, one partition, mounted under '/'
    DefaultConfig = """
- local_loop:
    name: image0
"""

# This is an example of the next level config
# mkfs:
#  base: root
#  type: ext4
#  mount_point: /

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
        self.plugin_manager = extension.ExtensionManager(
            namespace='diskimage_builder.block_device.plugin',
            invoke_on_load=False)

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

        for config_entry in config:
            if len(config_entry) != 1:
                logger.error("Invalid config entry: more than one key "
                             "on top level [%s]" % config_entry)
                raise BlockDeviceSetupException(
                    "Top level config must contain exactly one key per entry")
            logger.debug("Config entry [%s]" % config_entry)
            cfg_obj_name = list(config_entry.keys())[0]
            cfg_obj_val = config_entry[cfg_obj_name]

            # As the first step the configured objects are created
            # (if it exists)
            if cfg_obj_name not in self.plugin_manager:
                logger.error("Configured top level element [%s] "
                             "does not exists." % cfg_obj_name)
                return 1
            cfg_obj = self.plugin_manager[cfg_obj_name].plugin(
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
        if 'root' in result:
            print("%s" % result['root']['device'])
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
