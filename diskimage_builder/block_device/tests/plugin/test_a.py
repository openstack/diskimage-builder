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


class TestANode(NodeBase):
    def __init__(self, name):
        logger.debug("Create test 1")
        super(TestANode, self).__init__(name)

    def get_edges(self):
        # this is like the loop node; it's a root and doesn't have a
        # base
        return ([], [])

    def create(self, state, rollback):
        # put some fake entries into state
        state['test_a'] = {}
        state['test_a']['value'] = 'foo'
        state['test_a']['value2'] = 'bar'
        return


class TestA(PluginBase):

    def __init__(self, config, defaults):
        super(PluginBase, self).__init__()
        self.node = TestANode(config['name'])

    def get_nodes(self):
        return [self.node]
