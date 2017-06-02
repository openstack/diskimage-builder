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
    def __init__(self, config, state, test_rollback):
        logger.debug("Create test 1")
        super(TestANode, self).__init__(config['name'], state)
        # might be a root node, so possibly no base
        if 'base' in config:
            self.base = config['base']

        # put something in the state for test_b to check for
        state['test_init_state'] = 'here'

        # If we're doing rollback testing the config has some strings
        # set for us
        if test_rollback:
            self.add_rollback(self.do_rollback, config['rollback_one_arg'])
            self.add_rollback(self.do_rollback, config['rollback_two_arg'])
        # see if we're the node who is going to fail
        self.trigger_rollback = True if 'trigger_rollback' in config else False

    def get_edges(self):
        # may not have a base, if used as root node
        to = [self.base] if hasattr(self, 'base') else []
        return (to, [])

    def do_rollback(self, string):
        # We will check this after all rollbacks to make sure they ran
        # in the right order
        self.state['rollback_test'].append(string)

    def create(self):
        # put some fake entries into state
        self.state['test_a'] = {}
        self.state['test_a']['value'] = 'foo'
        self.state['test_a']['value2'] = 'bar'

        if self.trigger_rollback:
            # The rollback test will append the strings to this as
            # it unrolls, and we'll check it's value at the end
            self.state['rollback_test'] = []
            raise RuntimeError("Rollback triggered")

        return

    def umount(self):
        # Umount is run in reverse.  This key should exist from test_b
        self.state['umount'].append('test_a')


class TestA(PluginBase):

    def __init__(self, config, defaults, state):
        super(TestA, self).__init__()

        test_rollback = True if 'test_rollback' in defaults else False
        self.node = TestANode(config, state, test_rollback)

    def get_nodes(self):
        return [self.node]
