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
import collections
import json
import logging
import os
import pickle
import pprint
import shutil
import yaml

from diskimage_builder.block_device.config import config_tree_to_graph
from diskimage_builder.block_device.config import create_graph
from diskimage_builder.block_device.exception import \
    BlockDeviceSetupException
from diskimage_builder.block_device.utils import exec_sudo


logger = logging.getLogger(__name__)


def _load_json(file_name):
    """Load file from .json file on disk, return None if not existing"""
    if os.path.exists(file_name):
        with codecs.open(file_name, encoding="utf-8", mode="r") as fd:
            return json.load(fd)
    return None


class BlockDeviceState(collections.MutableMapping):
    """The global state singleton

    An reference to an instance of this object is saved into nodes as
    a global repository.  It wraps a single dictionary "state" and
    provides a few helper functions.

    The state ends up used in two contexts:

     - The node list (including this state) is pickled and dumped
       between cmd_create() and later cmd_* calls that need to call
       the nodes.

     - Some other cmd_* calls, such as cmd_writefstab, only need
       access to values inside the state and not the whole node list,
       and load it from the json dump created after cmd_create()
    """
    # XXX:
    #  - we could implement getters/setters such that if loaded from
    #    disk, the state is read-only? or make it append-only
    #    (i.e. you can't overwrite existing keys)
    def __init__(self, filename=None):
        """Initialise state

        :param filename: if :param:`filename` is passed and exists, it
          will be loaded as the state.  If it does not exist an
          exception is raised.  If :param:`filename` is not
          passed, state will be initalised to a blank dictionary.
        """
        if filename:
            if not os.path.exists(filename):
                raise BlockDeviceSetupException("State dump not found")
            else:
                self.state = _load_json(filename)
                assert self.state is not None
        else:
            self.state = {}

    def __delitem__(self, key):
        del self.state[key]

    def __getitem__(self, key):
        return self.state[key]

    def __setitem__(self, key, value):
        self.state[key] = value

    def __iter__(self):
        return iter(self.state)

    def __len__(self):
        return len(self.state)

    def save_state(self, filename):
        """Persist the state to disk

        :param filename: The file to persist state to
        """
        logger.debug("Writing state to: %s", filename)
        self.debug_dump()
        with open(filename, "w") as fd:
            json.dump(self.state, fd)

    def debug_dump(self):
        """Log state to debug"""
        # This is pretty good for human consumption, but maybe a bit
        # verbose.
        nice_output = pprint.pformat(self.state, width=40)
        for line in nice_output.split('\n'):
            logger.debug('{0:{fill}{align}50}'.format(
                line, fill=' ', align='<'))


class BlockDevice(object):
    """Handles block devices.

    This class handles the complete setup and deletion of all aspects
    of the block device level.

    A typical call sequence:

    cmd_init: initialize the block device level config.  After this
       call it is possible to e.g. query information from the (partially
       automatic generated) internal state like root-label.

    cmd_getval: retrieve information about the (internal) block device
       state like the block image device (for bootloader) or the
       root-label (for writing fstab).

    cmd_create: creates all the different aspects of the block
       device. When this call is successful, the complete block level
       device is set up, filesystems are created and are mounted at
       the correct position.
       After this call it is possible to copy / install all the needed
       files into the appropriate directories.

    cmd_writefstab: creates the (complete) fstab for the system.

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

    dib-block-device init ...
    # From that point the database can be queried, like
    ROOT_LABEL=$(dib-block-device getval root-label)

    Please note that currently the dib-block-device executable can
    only be used outside the chroot.

    dib-block-device create ...
    trap "dib-block-device delete ..." EXIT
    # copy / install files
    dib-block-device umount ...
    # convert image(s)
    dib-block-device cleanup ...
    trap - EXIT
    """

    def _merge_rootfs_params(self):
        """Merge rootfs related parameters into configuration

        To maintain compatability with some old block-device
        environment variables from before we had a specific
        block-device config, disk-image-create provides a "parameters"
        file that translates the old bash-environment variables into a
        YAML based configuration file (``self.params``).

        Here we merge the values in this parameters file that relate
        to the root file-system into the final configuration.  We look
        for the ``mkfs_root`` node in the new config, and pull the
        relevant settings from the parameters into it.

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
                            # The default label is "cloudimg-rootfs"
                            # for historical reasons (upstream
                            # images/EC2 defaults/cloud-init etc).  We
                            # want to remain backwards compatible, but
                            # unfortunately that's too long for XFS so
                            # we've decided on 'img-rootfs' in that
                            # case.  Note there's separate checks if
                            # the label is specified explicitly.
                            if v.get('type') == 'xfs':
                                v['label'] = 'img-rootfs'
                            else:
                                v['label'] = 'cloudimg-rootfs'

    def __init__(self, params):
        """Create BlockDevice object

        Arguments:
        :param params: YAML file from --params
        """

        logger.debug("Creating BlockDevice object")

        self.params = params
        logger.debug("Params [%s]", self.params)

        self.state_dir = os.path.join(
            self.params['build-dir'], "states/block-device")
        self.state_json_file_name \
            = os.path.join(self.state_dir, "state.json")
        self.config_json_file_name \
            = os.path.join(self.state_dir, "config.json")
        self.node_pickle_file_name \
            = os.path.join(self.state_dir, "nodes.pickle")

        self.config = _load_json(self.config_json_file_name)

        # This needs to exists for the state and config files
        try:
            os.makedirs(self.state_dir)
        except OSError:
            pass

    def cmd_init(self):
        """Initialize block device setup

        This initializes the block device setup layer. One major task
        is to parse and check the configuration, write it down for
        later examiniation and execution.
        """
        with open(self.params['config'], "rt") as config_fd:
            self.config = yaml.safe_load(config_fd)
        logger.debug("Config before merge [%s]", self.config)
        self.config = config_tree_to_graph(self.config)
        logger.debug("Config before merge [%s]", self.config)
        self._merge_rootfs_params()
        logger.debug("Final config [%s]", self.config)
        # Write the final config
        with open(self.config_json_file_name, "wt") as fd:
            json.dump(self.config, fd)
        logger.info("Wrote final block device config to [%s]",
                    self.config_json_file_name)

    def _config_get_mount(self, path):
        for entry in self.config:
            for k, v in entry.items():
                if k == 'mount' and v['mount_point'] == path:
                    return v
        assert False

    def _config_get_all_mount_points(self):
        rvec = []
        for entry in self.config:
            for k, v in entry.items():
                if k == 'mount':
                    rvec.append(v['mount_point'])
        return rvec

    def _config_get_mkfs(self, name):
        for entry in self.config:
            for k, v in entry.items():
                if k == 'mkfs' and v['name'] == name:
                    return v
        assert False

    def cmd_getval(self, symbol):
        """Retrieve value from block device level

        The value of SYMBOL is printed to stdout.  This is intended to
        be captured into bash-variables for backward compatibility
        (non python) access to internal configuration.

        Arguments:
        :param symbol: the symbol to get
        """
        logger.info("Getting value for [%s]", symbol)

        if symbol == "root-label":
            root_mount = self._config_get_mount("/")
            root_fs = self._config_get_mkfs(root_mount['base'])
            logger.debug("root-label [%s]", root_fs['label'])
            print("%s" % root_fs['label'])
            return 0

        if symbol == "root-fstype":
            root_mount = self._config_get_mount("/")
            root_fs = self._config_get_mkfs(root_mount['base'])
            logger.debug("root-fstype [%s]", root_fs['type'])
            print("%s" % root_fs['type'])
            return 0

        if symbol == 'mount-points':
            mount_points = self._config_get_all_mount_points()
            # we return the mountpoints joined by a pipe, because it is not
            # a valid char in directories, so it is a safe separator for the
            # mountpoints list
            print("%s" % "|".join(mount_points))
            return 0

        # the following symbols all come from the global state
        # dictionary.  They can only be accessed after the state has
        # been dumped; i.e. after cmd_create() called.
        state = BlockDeviceState(self.state_json_file_name)

        # The path to the .raw file for conversion
        if symbol == 'image-path':
            print("%s" % state['blockdev']['image0']['image'])
            return 0

        # This is the loopback device where the above image is setup
        if symbol == 'image-block-device':
            print("%s" % state['blockdev']['image0']['device'])
            return 0

        # Full list of created devices by name.  Some bootloaders, for
        # example, want to be able to see their boot partitions to
        # copy things in.  Intended to be read into a bash array
        if symbol == 'image-block-devices':
            out = ""
            for k, v in state['blockdev'].items():
                out += " [%s]=%s " % (k, v['device'])
            print(out)
            return 0

        logger.error("Invalid symbol [%s] for getval", symbol)
        return 1

    def cmd_writefstab(self):
        """Creates the fstab"""
        logger.info("Creating fstab")

        # State should have been created by prior calls; we only need
        # the dict
        state = BlockDeviceState(self.state_json_file_name)

        tmp_fstab = os.path.join(self.state_dir, "fstab")
        with open(tmp_fstab, "wt") as fstab_fd:
            # This gives the order in which this must be mounted
            for mp in state['mount_order']:
                logger.debug("Writing fstab entry for [%s]", mp)
                fs_base = state['mount'][mp]['base']
                fs_name = state['mount'][mp]['name']
                fs_val = state['filesys'][fs_base]
                if 'label' in fs_val:
                    diskid = "LABEL=%s" % fs_val['label']
                else:
                    diskid = "UUID=%s" % fs_val['uuid']

                # If there is no fstab entry - do not write anything
                if 'fstab' not in state:
                    continue
                if fs_name not in state['fstab']:
                    continue

                options = state['fstab'][fs_name]['options']
                dump_freq = state['fstab'][fs_name]['dump-freq']
                fsck_passno = state['fstab'][fs_name]['fsck-passno']

                fstab_fd.write("%s %s %s %s %s %s\n"
                               % (diskid, mp, fs_val['fstype'],
                                  options, dump_freq, fsck_passno))

        target_etc_dir = os.path.join(self.params['build-dir'], 'built', 'etc')
        exec_sudo(['mkdir', '-p', target_etc_dir])
        exec_sudo(['cp', tmp_fstab, os.path.join(target_etc_dir, "fstab")])

        return 0

    def cmd_create(self):
        """Creates the block device"""

        logger.info("create() called")
        logger.debug("Using config [%s]", self.config)

        # Create a new, empty state
        state = BlockDeviceState()
        try:
            dg, call_order = create_graph(self.config, self.params, state)
            for node in call_order:
                node.create()
        except Exception:
            logger.exception("Create failed; rollback initiated")
            reverse_order = reversed(call_order)
            for node in reverse_order:
                node.rollback()
            # save the state for debugging
            state.save_state(self.state_json_file_name)
            logger.error("Rollback complete, exiting")
            raise

        # dump state and nodes, in order
        # XXX: we only dump the call_order (i.e. nodes) not the whole
        #      graph here, because later calls do not need the graph
        #      at this stage.  might they?
        state.save_state(self.state_json_file_name)
        pickle.dump(call_order, open(self.node_pickle_file_name, 'wb'))

        logger.info("create() finished")
        return 0

    def cmd_umount(self):
        """Unmounts the blockdevice and cleanup resources"""

        # If the state is not here, cmd_cleanup removed it?  Nothing
        # more to do?
        #  XXX: better understand this...
        if not os.path.exists(self.node_pickle_file_name):
            logger.info("State already cleaned - no way to do anything here")
            return 0

        call_order = pickle.load(open(self.node_pickle_file_name, 'rb'))
        reverse_order = reversed(call_order)

        for node in reverse_order:
            node.umount()

        return 0

    def cmd_cleanup(self):
        """Cleanup all remaining relicts - in good case"""

        # Cleanup must be done in reverse order
        try:
            call_order = pickle.load(open(self.node_pickle_file_name, 'rb'))
        except IOError:
            raise BlockDeviceSetupException("Pickle file not found")

        reverse_order = reversed(call_order)

        for node in reverse_order:
            node.cleanup()

        logger.info("Removing temporary state dir [%s]", self.state_dir)
        shutil.rmtree(self.state_dir)

        return 0

    def cmd_delete(self):
        """Cleanup all remaining relicts - in case of an error"""

        # Deleting must be done in reverse order
        try:
            call_order = pickle.load(open(self.node_pickle_file_name, 'rb'))
        except IOError:
            raise BlockDeviceSetupException("Pickle file not found")
        reverse_order = reversed(call_order)

        for node in reverse_order:
            node.delete()

        logger.info("Removing temporary state dir [%s]", self.state_dir)
        shutil.rmtree(self.state_dir)

        return 0
