# Copyright 2016-2017 Andreas Florath (andreas@florath.net)
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

    cmd_init: initialized the block device level config.  After this
       call it is possible to e.g. query information from the (partially
       automatic generated) internal state like root-label.

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

    dib-block-device --phase=init ...
    # From that point the database can be queried, like
    ROOT_LABEL=$(dib-block-device --phase=getval --symbol=root-label ...)

    Please note that currently the dib-block-device executable can
    only be used outside the chroot.

    dib-block-device --phase=create ...
    trap "dib-block-device --phase=delete ..." EXIT
    # copy / install files
    dib-block-device --phase=umount ...
    # convert image(s)
    dib-block-device --phase=cleanup ...
    trap - EXIT
    """

    def _merge_into_config(self):
        """Merge old (default) config into new

        There is the need to be compatible using some old environment
        variables.  This is done in the way, that if there is no
        explicit value given, these values are inserted into the current
        configuration.
        """
        for entry in self.config:
            for k, v in entry.items():
                if k == 'mkfs':
                    if 'name' not in v:
                        continue
                    if v['name'] != 'mkfs_root':
                        continue
                    if 'type' not in v \
                       and 'root-fs-type' in self.params:
                        v['type'] = self.params['root-fs-type']
                    if 'opts' not in v \
                       and 'root-fs-opts' in self.params:
                        v['opts'] = self.params['root-fs-opts']
                    if 'label' not in v \
                       and 'root-label' in self.params:
                        if self.params['root-label'] is not None:
                            v['label'] = self.params['root-label']
                        else:
                            v['label'] = "cloudimg-rootfs"

    @staticmethod
    def _load_json(file_name):
        if os.path.exists(file_name):
            with codecs.open(file_name, encoding="utf-8", mode="r") as fd:
                return json.load(fd)
        return None

    def __init__(self, args):
        logger.debug("Creating BlockDevice object")
        logger.debug("Param file [%s]" % args.params)
        self.args = args

        with open(self.args.params) as param_fd:
            self.params = yaml.safe_load(param_fd)
        logger.debug("Params [%s]" % self.params)

        self.state_dir = os.path.join(
            self.params['build-dir'], "states/block-device")
        self.state_json_file_name \
            = os.path.join(self.state_dir, "state.json")
        self.plugin_manager = extension.ExtensionManager(
            namespace='diskimage_builder.block_device.plugin',
            invoke_on_load=False)
        self.config_json_file_name \
            = os.path.join(self.state_dir, "config.json")

        self.config = self._load_json(self.config_json_file_name)
        self.state = self._load_json(self.state_json_file_name)
        logger.debug("Using state [%s]", self.state)

        # This needs to exists for the state and config files
        try:
            os.makedirs(self.state_dir)
        except OSError:
            pass

    def write_state(self, state):
        logger.debug("Write state [%s]" % self.state_json_file_name)
        with open(self.state_json_file_name, "w") as fd:
            json.dump(state, fd)

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
        dg, call_order = self.create_graph(self.config, self.params)
        for node in call_order:
            node.create(result, rollback)

    def cmd_init(self):
        """Initialize block device setup

        This initializes the block device setup layer. One major task
        is to parse and check the configuration, write it down for
        later examiniation and execution.
        """
        with open(self.params['config'], "rt") as config_fd:
            self.config = yaml.safe_load(config_fd)
        logger.debug("Config before merge [%s]" % self.config)
        self._merge_into_config()
        logger.debug("Final config [%s]" % self.config)
        # Write the final config
        with open(self.config_json_file_name, "wt") as fd:
            json.dump(self.config, fd)
        logger.info("Wrote final block device config to [%s]"
                    % self.config_json_file_name)

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

    def cmd_umount(self):
        """Unmounts the blockdevice and cleanup resources"""

        dg, call_order = self.create_graph(self.config, self.params)
        reverse_order = reversed(call_order)
        if dg is None:
            return 0
        for node in reverse_order:
            node.umount(self.state)

        # To be compatible with the current implementation, echo the
        # result to stdout.
        print("%s" % self.state['image0']['image'])

        return 0

    def cmd_cleanup(self):
        """Cleanup all remaining relicts - in good case"""

        # Deleting must be done in reverse order
        dg, call_order = self.create_graph(self.config, self.params)
        reverse_order = reversed(call_order)

        if dg is None:
            return 0
        for node in reverse_order:
            node.cleanup(self.state)

        logger.info("Removing temporary dir [%s]" % self.state_dir)
        shutil.rmtree(self.state_dir)

        return 0

    def cmd_delete(self):
        """Cleanup all remaining relicts - in case of an error"""

        # Deleting must be done in reverse order
        dg, call_order = self.create_graph(self.config, self.params)
        reverse_order = reversed(call_order)

        if dg is None:
            return 0
        for node in reverse_order:
            node.delete(self.state)

        logger.info("Removing temporary dir [%s]" % self.state_dir)
        shutil.rmtree(self.state_dir)

        return 0
