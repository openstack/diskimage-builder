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

from diskimage_builder.block_device.exception import \
    BlockDeviceSetupException
from diskimage_builder.block_device.plugin import NodeBase


logger = logging.getLogger(__name__)


class PartitionNode(NodeBase):

    flag_boot = 1
    flag_primary = 2

    def __init__(self, config, state, parent, prev_partition):

        super(PartitionNode, self).__init__(config['name'], state)

        self.base = config['base']
        self.partitioning = parent
        self.prev_partition = prev_partition

        # filter out some MBR only options for clarity
        if self.partitioning.label == 'gpt':
            if 'flags' in config and 'primary' in config['flags']:
                raise BlockDeviceSetupException(
                    "Primary flag not supported for GPT partitions")

        self.flags = set()
        if 'flags' in config:
            for f in config['flags']:
                if f == 'boot':
                    self.flags.add(self.flag_boot)
                elif f == 'primary':
                    self.flags.add(self.flag_primary)
                else:
                    raise BlockDeviceSetupException("Unknown flag: %s" % f)

        if 'size' not in config:
            raise BlockDeviceSetupException("No size in partition" % self.name)
        self.size = config['size']

        if self.partitioning.label == 'gpt':
            self.ptype = str(config['type']) if 'type' in config else '8300'
        elif self.partitioning.label == 'mbr':
            self.ptype = int(config['type'], 16) if 'type' in config else 0x83

    def get_flags(self):
        return self.flags

    def get_size(self):
        return self.size

    def get_type(self):
        return self.ptype

    def get_edges(self):
        edge_from = [self.base]
        edge_to = []
        if self.prev_partition is not None:
            edge_from.append(self.prev_partition.name)
        return (edge_from, edge_to)

    # These all call back to the parent "partitioning" object to do
    # the real work.  Every node calls it, but only one will succeed;
    # see the gating we do in the parent function.
    #
    # XXX: A better model here would be for the parent object to a
    # real node in the config graph, so it's create() gets called.
    # These can then just be stubs.
    def create(self):
        self.partitioning.create()

    def umount(self):
        self.partitioning.umount()

    def cleanup(self):
        self.partitioning.cleanup()
