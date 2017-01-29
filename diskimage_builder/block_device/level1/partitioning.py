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

from subprocess import CalledProcessError

from diskimage_builder.block_device.blockdevice import \
    BlockDeviceSetupException
from diskimage_builder.block_device.level1.mbr import MBR
from diskimage_builder.block_device.plugin_base import PluginBase
from diskimage_builder.block_device.tree_config import TreeConfig
from diskimage_builder.block_device.utils import exec_sudo
from diskimage_builder.block_device.utils import parse_abs_size_spec
from diskimage_builder.block_device.utils import parse_rel_size_spec
from diskimage_builder.graph.digraph import Digraph


logger = logging.getLogger(__name__)


class PartitionTreeConfig(object):

    @staticmethod
    def config_tree_to_digraph(config_key, config_value, pconfig, dconfig,
                               base_name, plugin_manager):
        logger.debug("called [%s] [%s] [%s]"
                     % (config_key, config_value, base_name))
        assert config_key == Partition.type_string

        for partition in config_value:
            name = partition['name']
            nconfig = {'name': name}
            for k, v in partition.items():
                if k not in plugin_manager:
                    nconfig[k] = v
                else:
                    plugin_manager[k].plugin \
                                     .tree_config.config_tree_to_digraph(
                                         k, v, dconfig, name, plugin_manager)
            pconfig.append(nconfig)

        logger.debug("finished [%s] [%s]" % (nconfig, dconfig))


class Partition(Digraph.Node):

    type_string = "partitions"
    tree_config = TreeConfig("partitions")

    def __init__(self, name, flags, size, ptype, base, partitioning,
                 prev_partition):
        Digraph.Node.__init__(self, name)
        self.name = name
        self.flags = flags
        self.size = size
        self.ptype = ptype
        self.base = base
        self.partitioning = partitioning
        self.prev_partition = prev_partition

    def __repr__(self):
        return "<Partition [%s] on [%s] size [%s] prev [%s]>" \
            % (self.name, self.base, self.size,
               self.prev_partition.name if self.prev_partition else "UNSET")

    def get_flags(self):
        return self.flags

    def get_size(self):
        return self.size

    def get_type(self):
        return self.ptype

    def get_name(self):
        return self.name

    def insert_edges(self, dg):
        bnode = dg.find(self.base)
        assert bnode is not None
        dg.create_edge(bnode, self)
        if self.prev_partition is not None:
            logger.debug("Insert edge [%s]" % self)
            dg.create_edge(self.prev_partition, self)

    def create(self, result, rollback):
        self.partitioning.create(result, rollback)

    def umount(self, state):
        """Partitioning does not need any umount task."""
        pass

    def cleanup(self, state):
        """Partitioning does not need any cleanup."""
        pass

    def delete(self, state):
        """Partitioning does not need any cleanup."""
        pass


class PartitioningTreeConfig(object):

    @staticmethod
    def config_tree_to_digraph(config_key, config_value, dconfig,
                               default_base_name, plugin_manager):
        logger.debug("called [%s] [%s] [%s]"
                     % (config_key, config_value, default_base_name))
        assert config_key == "partitioning"
        base_name = config_value['base'] if 'base' in config_value \
                    else default_base_name
        nconfig = {'base': base_name}
        for k, v in config_value.items():
            if k != 'partitions':
                nconfig[k] = v
            else:
                pconfig = []
                PartitionTreeConfig.config_tree_to_digraph(
                    k, v, pconfig, dconfig, base_name, plugin_manager)
                nconfig['partitions'] = pconfig

        dconfig.append({config_key: nconfig})
        logger.debug("finished new [%s] complete [%s]" % (nconfig, dconfig))


class Partitioning(PluginBase):

    tree_config = PartitioningTreeConfig()

    flag_boot = 1
    flag_primary = 2

    def __init__(self, config, default_config):
        logger.debug("Creating Partitioning object; config [%s]" % config)
        # Because using multiple partitions of one base is done
        # within one object, there is the need to store a flag if the
        # creation of the partitions was already done.
        self.already_created = False

        # Parameter check
        if 'base' not in config:
            self._config_error("Partitioning config needs 'base'")
        self.base = config['base']

        if 'label' not in config:
            self._config_error("Partitioning config needs 'label'")
        self.label = config['label']
        if self.label not in ("mbr", ):
            self._config_error("Label must be 'mbr'")

        # It is VERY important to get the alignment correct. If this
        # is not correct, the disk performance might be very poor.
        # Example: In some tests a 'off by one' leads to a write
        # performance of 30% compared to a correctly aligned
        # partition.
        # The problem for DIB is, that it cannot assume that the host
        # system uses the same IO sizes as the target system,
        # therefore here a fixed approach (as used in all modern
        # systems with large disks) is used.  The partitions are
        # aligned to 1MiB (which are about 2048 times 512 bytes
        # blocks)
        self.align = 1024 * 1024  # 1MiB as default
        if 'align' in config:
            self.align = parse_abs_size_spec(config['align'])

        if 'partitions' not in config:
            self._config_error("Partitioning config needs 'partitions'")

        self.partitions = []
        prev_partition = None

        for part_cfg in config['partitions']:
            if 'name' not in part_cfg:
                self.config_error("Missing 'name' in partition config")
            part_name = part_cfg['name']

            flags = set()
            if 'flags' in part_cfg:
                for f in part_cfg['flags']:
                    if f == 'boot':
                        flags.add(Partitioning.flag_boot)
                    elif f == 'primary':
                        flags.add(Partitioning.flag_primary)
                    else:
                        self._config_error("Unknown flag [%s] in "
                                           "partitioning for [%s]"
                                           % (f, part_name))
            if 'size' not in part_cfg:
                self._config_error("No 'size' in partition [%s]"
                                   % part_name)
            size = part_cfg['size']

            ptype = int(part_cfg['type'], 16) if 'type' in part_cfg else 0x83

            np = Partition(part_name, flags, size, ptype, self.base, self,
                           prev_partition)
            self.partitions.append(np)
            prev_partition = np
            logger.debug(part_cfg)

    def _config_error(self, msg):
        logger.error(msg)
        raise BlockDeviceSetupException(msg)

    def _size_of_block_dev(self, dev):
        with open(dev, "r") as fd:
            fd.seek(0, 2)
            return fd.tell()

    def insert_nodes(self, dg):
        for part in self.partitions:
            logger.debug("Insert node [%s]" % part)
            dg.add_node(part)

    def _all_part_devices_exist(self, expected_part_devices):
        for part_device in expected_part_devices:
            logger.debug("Checking if partition device [%s] exists" %
                         part_device)
            if not os.path.exists(part_device):
                logger.info("Partition device [%s] does not exists"
                            % part_device)
                return False
            logger.debug("Partition already exists [%s]" % part_device)
        return True

    def _notify_os_of_partition_changes(self, device_path, partition_devices):
        """Notify of of partition table changes

        There is the need to call some programs to inform the operating
        system of partition tables changes.
        These calls are highly distribution and version specific. Here
        a couple of different methods are used to get the best result.
        """
        try:
            exec_sudo(["partprobe", device_path])
            exec_sudo(["udevadm", "settle"])
        except CalledProcessError as e:
            logger.info("Ignoring settling failure: %s" % e)
            pass

        if self._all_part_devices_exist(partition_devices):
            return
        # If running inside Docker, make our nodes manually, because udev
        # will not be working.
        if os.path.exists("/.dockerenv"):
            # kpartx cannot run in sync mode in docker.
            exec_sudo(["kpartx", "-av", device_path])
            exec_sudo(["dmsetup", "--noudevsync", "mknodes"])
            return

        exec_sudo(["kpartx", "-avs", device_path])

    def create(self, result, rollback):
        image_path = result['blockdev'][self.base]['image']
        device_path = result['blockdev'][self.base]['device']
        logger.info("Creating partition on [%s] [%s]" %
                    (self.base, image_path))

        if self.already_created:
            logger.info("Not creating the partitions a second time.")
            return

        assert self.label == 'mbr'

        partition_devices = set()
        disk_size = self._size_of_block_dev(image_path)
        with MBR(image_path, disk_size, self.align) as part_impl:
            for part_cfg in self.partitions:
                part_name = part_cfg.get_name()
                part_bootflag = Partitioning.flag_boot \
                                in part_cfg.get_flags()
                part_primary = Partitioning.flag_primary \
                               in part_cfg.get_flags()
                part_size = part_cfg.get_size()
                part_free = part_impl.free()
                part_type = part_cfg.get_type()
                logger.debug("Not partitioned space [%d]" % part_free)
                part_size = parse_rel_size_spec(part_size,
                                                part_free)[1]
                part_no \
                    = part_impl.add_partition(part_primary, part_bootflag,
                                              part_size, part_type)
                logger.debug("Create partition [%s] [%d]" %
                             (part_name, part_no))
                partition_device_name = device_path + "p%d" % part_no
                result['blockdev'][part_name] \
                    = {'device': partition_device_name}
                partition_devices.add(partition_device_name)

        self.already_created = True
        self._notify_os_of_partition_changes(device_path, partition_devices)
        return
