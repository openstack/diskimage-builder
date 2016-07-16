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

from diskimage_builder.block_device.blockdevicesetupexception \
    import BlockDeviceSetupException
from diskimage_builder.block_device.level1.mbr import MBR
from diskimage_builder.block_device.utils import parse_abs_size_spec
from diskimage_builder.block_device.utils import parse_rel_size_spec
from diskimage_builder.graph.digraph import Digraph
import logging


logger = logging.getLogger(__name__)


class Partition(Digraph.Node):

    def __init__(self, name, flags, size, ptype, base, partitioning):
        Digraph.Node.__init__(self, name)
        self.flags = flags
        self.size = size
        self.ptype = ptype
        self.base = base
        self.partitioning = partitioning

    def get_flags(self):
        return self.flags

    def get_size(self):
        return self.size

    def get_type(self):
        return self.ptype

    def insert_edges(self, dg):
        bnode = dg.find(self.base)
        assert bnode is not None
        dg.create_edge(bnode, self)

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


class Partitioning(object):

    type_string = "partitioning"

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

        self.partitions = {}
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

            self.partitions[part_name] \
                = Partition(part_name, flags, size, ptype, self.base, self)
            logger.debug(part_cfg)

    def _config_error(self, msg):
        logger.error(msg)
        raise BlockDeviceSetupException(msg)

    def _size_of_block_dev(self, dev):
        with open(dev, "r") as fd:
            fd.seek(0, 2)
            return fd.tell()

    def insert_nodes(self, dg):
        for _, part in self.partitions.items():
            dg.add_node(part)

    def create(self, result, rollback):
        image_path = result[self.base]['image']
        device_path = result[self.base]['device']
        logger.info("Creating partition on [%s] [%s]" %
                    (self.base, image_path))

        if self.already_created:
            logger.info("Not creating the partitions a second time.")
            return

        assert self.label == 'mbr'

        disk_size = self._size_of_block_dev(image_path)
        with MBR(image_path, disk_size, self.align) as part_impl:
            for part_name, part_cfg in self.partitions.items():
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
                result[part_name] = {'device': device_path + "p%d" % part_no}

        self.already_created = True
        return
