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

import testtools

from diskimage_builder.graph.digraph import Digraph
from diskimage_builder.graph.digraph import digraph_create_from_dict
from diskimage_builder.graph.digraph import node_list_to_node_name_list


class TestTopologicalSearch(testtools.TestCase):

    def test_tsort_001(self):
        """Simple three node digraph"""

        dg = digraph_create_from_dict(
            {"A": ["B", "C"], "B": ["C"], "C": []})
        tsort = dg.topological_sort()
        tnames = node_list_to_node_name_list(tsort)
        self.assertEqual(tnames, ['A', 'B', 'C'], "incorrect")

    def test_tsort_002(self):
        """Zero node digraph"""

        dg = digraph_create_from_dict({})
        tsort = dg.topological_sort()
        tnames = node_list_to_node_name_list(tsort)
        self.assertEqual(tnames, [], "incorrect")

    def test_tsort_003(self):
        """One node digraph"""

        dg = digraph_create_from_dict({"A": []})
        tsort = dg.topological_sort()
        tnames = node_list_to_node_name_list(tsort)
        self.assertEqual(tnames, ["A"], "incorrect")

    def test_tsort_004(self):
        """More complex digraph"""

        dg = digraph_create_from_dict(
            {"A": ["B", "C"], "B": ["C", "E"], "C": ["D", "E"],
             "D": ["E"], "E": []})
        tsort = dg.topological_sort()
        tnames = node_list_to_node_name_list(tsort)
        self.assertEqual(tnames, ['A', 'B', 'C', 'D', 'E'], "incorrect")

    def test_tsort_005(self):
        """Digraph with two components"""

        dg = digraph_create_from_dict({"A": ["B", "C"], "B": ["C"], "C": [],
                                       "D": ["E"], "E": []})
        tsort = dg.topological_sort()
        tnames = node_list_to_node_name_list(tsort)
        # Because of two components, there exist a couple of different
        # possibilities - but these are all the requirements that have
        # to be fulfilled to be a correct topological sort:
        self.assertTrue(tnames.index('A') < tnames.index('B'))
        self.assertTrue(tnames.index('B') < tnames.index('C'))
        self.assertTrue(tnames.index('D') < tnames.index('E'))

    def test_tsort_006(self):
        """Complex digraph with weights"""

        digraph = Digraph()
        node0 = Digraph.Node("R")
        digraph.add_node(node0)
        node1 = Digraph.Node("A")
        digraph.add_node(node1)
        node2 = Digraph.Node("B")
        digraph.add_node(node2)
        node3 = Digraph.Node("C")
        digraph.add_node(node3)
        node4 = Digraph.Node("B1")
        digraph.add_node(node4)
        node5 = Digraph.Node("B2")
        digraph.add_node(node5)
        node6 = Digraph.Node("B3")
        digraph.add_node(node6)

        digraph.create_edge(node0, node1, 1)
        digraph.create_edge(node0, node2, 2)
        digraph.create_edge(node0, node3, 3)

        digraph.create_edge(node2, node4, 7)
        digraph.create_edge(node2, node5, 14)
        digraph.create_edge(node2, node6, 21)

        tsort = digraph.topological_sort()
        tnames = node_list_to_node_name_list(tsort)

        # Also here: many possible solutions
        self.assertTrue(tnames.index('R') < tnames.index('A'))
        self.assertTrue(tnames.index('R') < tnames.index('B'))
        self.assertTrue(tnames.index('R') < tnames.index('C'))
        self.assertTrue(tnames.index('B') < tnames.index('B1'))
        self.assertTrue(tnames.index('B') < tnames.index('B2'))
        self.assertTrue(tnames.index('B') < tnames.index('B3'))

        # In addition in the weighted graph the following
        # must also hold:
        self.assertTrue(tnames.index('B') < tnames.index('A'))
        self.assertTrue(tnames.index('C') < tnames.index('B'))
        self.assertTrue(tnames.index('B2') < tnames.index('B1'))
        self.assertTrue(tnames.index('B3') < tnames.index('B2'))
