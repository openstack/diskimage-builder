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

from diskimage_builder.block_device.blockdevice \
    import BlockDeviceSetupException
from diskimage_builder.block_device.tree_config import TreeConfig
from diskimage_builder.graph.digraph import Digraph


logger = logging.getLogger(__name__)


class Fstab(Digraph.Node):

    type_string = "fstab"
    tree_config = TreeConfig("fstab")

    def _config_error(self, msg):
        logger.error(msg)
        raise BlockDeviceSetupException(msg)

    def __init__(self, config, params):
        logger.debug("Fstab object; config [%s]" % config)
        self.config = config
        self.params = params
        self.name = self.config['name']
        self.base = self.config['base']
        Digraph.Node.__init__(self, self.name)

        self.options = self.config.get('options', 'defaults')
        self.dump_freq = self.config.get('dump-freq', 0)
        self.fsck_passno = self.config.get('fsck-passno', 2)

    def insert_nodes(self, dg):
        logger.debug("Insert node")
        dg.add_node(self)

    def insert_edges(self, dg):
        logger.debug("Insert edge [%s]" % self)
        bnode = dg.find(self.base)
        assert bnode is not None
        dg.create_edge(bnode, self)

    def create(self, result, rollback):
        logger.debug("fstab create called [%s]" % self.name)
        logger.debug("result [%s]" % result)

        if 'fstab' not in result:
            result['fstab'] = {}

        result['fstab'][self.base] = {
            'name': self.name,
            'base': self.base,
            'options': self.options,
            'dump-freq': self.dump_freq,
            'fsck-passno': self.fsck_passno
        }

    def umount(self, state):
        """Fstab does not need any umount task."""
        pass

    def cleanup(self, state):
        """Fstab does not need any cleanup."""
        pass

    def delete(self, state):
        """Fstab does not need any cleanup."""
        pass
