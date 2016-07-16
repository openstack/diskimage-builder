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

from diskimage_builder.graph.digraph import Digraph
from diskimage_builder.graph.digraph import digraph_create_from_dict
import testtools


class TestDigraph(testtools.TestCase):

    def test_constructor_001(self):
        """Test conversion from dictionary to graph and back (two nodes)"""

        d = {"A": ["B"], "B": []}
        dg = digraph_create_from_dict(d)
        e = dg.as_dict()
        self.assertEqual(d["A"], list(e["A"]))

    def test_constructor_002(self):
        """Test conversion from dictionary to graph and back (zero nodes)"""

        d = {}
        dg = digraph_create_from_dict(d)
        e = dg.as_dict()
        self.assertEqual(d, e)

    def test_constructor_003(self):
        """Test conversion from dictionary to graph and back (one node)"""

        d = {"A": []}
        dg = digraph_create_from_dict(d)
        e = dg.as_dict()
        self.assertEqual(d["A"], list(e["A"]))

    def test_constructor_004(self):
        """Test conversion from dictionary to graph and back (one node)"""

        d = {"A": ["A"]}
        dg = digraph_create_from_dict(d)
        e = dg.as_dict()
        self.assertEqual(d["A"], list(e["A"]))

    def test_constructor_005(self):
        """Test conversion: error: pointed node does not exists"""

        d = {"A": ["B"]}
        try:
            d = digraph_create_from_dict(d)
            self.assertTrue(False)
        except RuntimeError:
            pass

    def test_constructor_006(self):
        """Test conversion from dictionary: two node circle"""

        d = {"A": ["B"], "B": ["A"]}
        dg = digraph_create_from_dict(d)
        e = dg.as_dict()
        self.assertEqual(d["A"], list(e["A"]))
        self.assertEqual(d["B"], list(e["B"]))

    def test_constructor_007(self):
        """Test conversion from dictionary: more complex graph"""

        d = {"A": ["B"], "B": ["A", "D", "C"], "C": ["A", "D"],
             "D": ["D"]}
        dg = digraph_create_from_dict(d)
        e = dg.as_dict()
        self.assertEqual(d['A'], list(e['A']))
        self.assertEqual(set(d['B']), set(e['B']))
        self.assertEqual(set(d['C']), set(e['C']))
        self.assertEqual(d['D'], list(e['D']))

    def test_find_01(self):
        """Digraph find with element available"""

        d = {"A": ["B"], "B": ["A", "C", "D"], "C": ["A", "D"],
             "D": ["D"]}
        dg = digraph_create_from_dict(d)
        n = dg.find("A")
        self.assertEqual("A", n.get_name(),)

    def test_find_02(self):
        """Digraph find with element not available"""

        d = {"A": ["B"], "B": ["A", "C", "D"], "C": ["A", "D"],
             "D": ["D"]}
        dg = digraph_create_from_dict(d)
        n = dg.find("Z")
        self.assertIsNone(n)

    def test_get_named_node_01(self):
        """Digraph get named node with map available"""

        d = {"A": ["B"], "B": ["A", "C", "D"], "C": ["A", "D"],
             "D": ["D"]}
        dg = digraph_create_from_dict(d)
        n = dg.find("A")
        self.assertEqual("A", n.get_name())

    def test_add_node_01(self):
        """Digraph add node with two times same name"""

        dg = Digraph()
        n1 = Digraph.Node("myname")
        n2 = Digraph.Node("myname")
        dg.add_node(n1)
        try:
            dg.add_node(n2)
            self.assertTrue(False)
        except RuntimeError:
            pass
