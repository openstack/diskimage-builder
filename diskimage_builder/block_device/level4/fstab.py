# Copyright 2017 Andreas Florath (andreas@florath.net)
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

from diskimage_builder.block_device.plugin import NodeBase
from diskimage_builder.block_device.plugin import PluginBase


logger = logging.getLogger(__name__)


class FstabNode(NodeBase):
    def __init__(self, config, state):
        super(FstabNode, self).__init__(config['name'], state)
        self.base = config['base']
        self.options = config.get('options', 'defaults')
        self.dump_freq = config.get('dump-freq', 0)
        self.fsck_passno = config.get('fsck-passno', 2)

    def get_edges(self):
        edge_from = [self.base]
        edge_to = []
        return (edge_from, edge_to)

    def create(self):
        logger.debug("fstab create called [%s]", self.name)

        if 'fstab' not in self.state:
            self.state['fstab'] = {}

        self.state['fstab'][self.base] = {
            'name': self.name,
            'base': self.base,
            'options': self.options,
            'dump-freq': self.dump_freq,
            'fsck-passno': self.fsck_passno
        }


class Fstab(PluginBase):
    def __init__(self, config, defaults, state):
        super(Fstab, self).__init__()

        self.node = FstabNode(config, state)

    def get_nodes(self):
        return [self.node]
