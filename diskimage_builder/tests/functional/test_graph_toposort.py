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

from diskimage_builder.graph.digraph import digraph_create_from_dict
from diskimage_builder.graph.digraph import node_list_to_node_name_list
import testtools


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
