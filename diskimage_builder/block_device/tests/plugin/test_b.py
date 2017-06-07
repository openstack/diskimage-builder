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

# plugin test case

import logging

from diskimage_builder.block_device.plugin import NodeBase
from diskimage_builder.block_device.plugin import PluginBase


logger = logging.getLogger(__name__)


class TestBNode(NodeBase):
    def __init__(self, name, base):
        logger.debug("Create test 1")
        super(TestBNode, self).__init__(name)
        self.base = base

    def get_edges(self):
        return ([self.base], [])

    def create(self, state, rollback):
        state['test_b'] = {}
        state['test_b']['value'] = 'baz'
        return


class TestB(PluginBase):

    def __init__(self, config, defaults):
        super(TestB, self).__init__()
        self.node = TestBNode(config['name'],
                              config['base'])

    def get_nodes(self):
        return [self.node]
