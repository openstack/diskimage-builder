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

from diskimage_builder.block_device.config import config_tree_to_graph
from diskimage_builder.block_device.config import create_graph
from diskimage_builder.block_device.exception import \
    BlockDeviceSetupException
from diskimage_builder.block_device.tests.test_base import TestBase


logger = logging.getLogger(__name__)


class TestConfig(TestBase):
    """Helper for setting up and reading a config"""
    def setUp(self):
        super(TestConfig, self).setUp()
        # previously we mocked some globals here ...


class TestGraphGeneration(TestConfig):
    """Extra helper class for testing graph generation"""
    def setUp(self):
        super(TestGraphGeneration, self).setUp()

        self.fake_default_config = {
            'build-dir': '/fake',
            'image-size': '1000',
            'image-dir': '/fake',
            'mount-base': '/fake',
        }


class TestConfigParsing(TestConfig):
    """Test parsing config file into a graph"""

    # test an entry in the config not being a valid plugin
    def test_config_bad_plugin(self):
        config = self.load_config_file('bad_plugin.yaml')
        self.assertRaises(BlockDeviceSetupException,
                          config_tree_to_graph,
                          config)

    # test a config that has multiple keys for a top-level entry
    def test_config_multikey_node(self):
        config = self.load_config_file('multi_key_node.yaml')
        self.assertRaisesRegex(BlockDeviceSetupException,
                               "Config entry top-level should be a single "
                               "dict:",
                               config_tree_to_graph,
                               config)

    # a graph should remain the same
    def test_graph(self):
        graph = self.load_config_file('simple_graph.yaml')
        parsed_graph = config_tree_to_graph(graph)
        self.assertItemsEqual(parsed_graph, graph)

    # equivalence of simple tree to graph
    def test_simple_tree(self):
        tree = self.load_config_file('simple_tree.yaml')
        graph = self.load_config_file('simple_graph.yaml')
        parsed_graph = config_tree_to_graph(tree)
        self.assertItemsEqual(parsed_graph, graph)

    # equivalence of a deeper tree to graph
    def test_deep_tree(self):
        tree = self.load_config_file('deep_tree.yaml')
        graph = self.load_config_file('deep_graph.yaml')
        parsed_graph = config_tree_to_graph(tree)
        self.assertItemsEqual(parsed_graph, graph)

    # equivalence of a complicated multi-partition tree to graph
    def test_multipart_tree(self):
        tree = self.load_config_file('multiple_partitions_tree.yaml')
        graph = self.load_config_file('multiple_partitions_graph.yaml')
        parsed_graph = config_tree_to_graph(tree)
        logger.debug(parsed_graph)
        self.assertItemsEqual(parsed_graph, graph)


class TestCreateGraph(TestGraphGeneration):

    # Test a graph with bad edge pointing to an invalid node
    def test_invalid_missing(self):
        config = self.load_config_file('bad_edge_graph.yaml')
        self.assertRaisesRegex(BlockDeviceSetupException,
                               "Edge not defined: this_is_not_a_node",
                               create_graph,
                               config, self.fake_default_config, {})

    # Test a graph with bad edge pointing to an invalid node
    def test_duplicate_name(self):
        config = self.load_config_file('duplicate_name.yaml')
        self.assertRaisesRegex(BlockDeviceSetupException,
                               "Duplicate node name: "
                               "this_is_a_duplicate",
                               create_graph,
                               config, self.fake_default_config, {})

    # Test digraph generation from deep_graph config file
    def test_deep_graph_generator(self):
        config = self.load_config_file('deep_graph.yaml')

        graph, call_order = create_graph(config, self.fake_default_config, {})

        call_order_list = [n.name for n in call_order]

        # manually created from deep_graph.yaml
        # Note unlike below, the sort here is stable because the graph
        # doesn't have multiple paths with only one partition
        call_order_names = ['image0', 'root', 'mkfs_root',
                            'mount_mkfs_root',
                            'fstab_mount_mkfs_root']

        self.assertListEqual(call_order_list, call_order_names)

    # Test multiple partition digraph generation
    def test_multiple_partitions_graph_generator(self):
        config = self.load_config_file('multiple_partitions_graph.yaml')

        graph, call_order = create_graph(config, self.fake_default_config, {})
        call_order_list = [n.name for n in call_order]

        # The sort creating call_order_list is unstable.

        # We want to ensure we see the "partitions" object in
        # root->var->var_log order
        root_pos = call_order_list.index('root')
        var_pos = call_order_list.index('var')
        var_log_pos = call_order_list.index('var_log')
        self.assertGreater(var_pos, root_pos)
        self.assertGreater(var_log_pos, var_pos)

        # Ensure mkfs happens after partition
        mkfs_root_pos = call_order_list.index('mkfs_root')
        self.assertLess(root_pos, mkfs_root_pos)
        mkfs_var_pos = call_order_list.index('mkfs_var')
        self.assertLess(var_pos, mkfs_var_pos)
        mkfs_var_log_pos = call_order_list.index('mkfs_var_log')
        self.assertLess(var_log_pos, mkfs_var_log_pos)
