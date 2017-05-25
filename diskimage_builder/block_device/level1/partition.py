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

    def __init__(self, config, parent, prev_partition):

        super(PartitionNode, self).__init__(config['name'])

        self.base = config['base']
        self.partitioning = parent
        self.prev_partition = prev_partition

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

    def create(self, result, rollback):
        self.partitioning.create(result, rollback)
