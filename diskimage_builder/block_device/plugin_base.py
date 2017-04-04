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

import abc
from diskimage_builder.graph.digraph import Digraph
import six


@six.add_metaclass(abc.ABCMeta)
class PluginBase(object):
    """Abstract base class for block device plugins"""

    def __init__(self, name):
        """All plugins must have a name"""
        self.name = name

    @abc.abstractmethod
    def create(self, state, rollback):
        """Create the block device plugin

        :param state: a dictionary to store results for this plugin.
                      These are used in two scenarios: other plugins
                      can use this to get information about the
                      result of the plugin and it can be used in
                      later runs of dib-block-device for cleaning up.
        :type state: dict(str:?)

        :param rollback: a list of python functions that will be
                         called in reversed order to cleanup if there
                         occurs an error later within the same
                         dib-block-device run.
        :type rollback: list(function)
        """


class NodePluginBase(PluginBase, Digraph.Node):

    def insert_nodes(self, dg):
        """Adds self as a node to the given digraph"""
        dg.add_node(self)
