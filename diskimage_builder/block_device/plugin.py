#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import abc
import six

#
# Plugins convert configuration entries into graph nodes ready for
# processing.  This defines the abstract classes for both.
#


@six.add_metaclass(abc.ABCMeta)
class NodeBase(object):
    """A configuration node entry

    This is the main driver class for dib-block-device operation.

    The final operations graph is composed of instantiations of this
    class.  The graph undergoes a topological sort (i.e. is linearised
    in dependency order) and each node has :func:`create` called in
    order to perform its operations.

    Every node has a unique string ``name``.  This is its key in the
    graph and used for edge relationships.  Implementations must
    ensure they initalize it; e.g.

    .. code-block:: python

       class FooNode(NodeBase):
           def __init__(name, arg1, ...):
               super(FooNode, self).__init__(name)

    """
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name

    @abc.abstractmethod
    def get_edges(self):
        """Return the dependencies/edges for this node

        This function will be called after all nodes are created (this
        is because some plugins need to know the global state of all
        nodes to decide their dependencies).

        This function returns a tuple with two lists

         * ``edges_from`` : a list of node names that point to us
         * ``edges_to`` : a list of node names we point to

        In most cases, node creation will have saved a single parent
        that was given in the ``base`` parameter of the configuration.
        A usual return might look like:

        .. code-block:: python

           def get_edges(self):
               return ( [self.base], [] )

        Some nodes (``level0``) don't have a base, however
        """
        return

    @abc.abstractmethod
    def create(self, results, rollback):
        """Main creation driver

        This is the main driver function.  After the graph is
        linearised, each node has it's :func:`create` function called.

        Arguments:

        :param results: A shared dictionary of prior results.  This
          dictionary is passed by reference to each call, meaning any
          entries inserted will be available to subsequent :func:`create`
          calls of following nodes.

        :param rollback: A shared list of functions to be called in
          the failure case.  Nodes should only append to this list.
          On failure, the callbacks will be processed in reverse
          order.

        :raises Exception: A failure should raise an exception.  This
          will initiate the rollback

        :return: None
        """
        return

    def umount(self, state):
        """Umount actions

        Actions to taken when ``dib-block-device umount`` is called

        :param state: the current state dictionary.  This is the
          `results` dictionary from :func:`create` before this call is
          made.
        :return: None
        """
        return

    def cleanup(self, state):
        """Cleanup actions

        Actions to taken when ``dib-block-device cleanup`` is called.
        This is the cleanup path in the *success* case.  The nodes are
        called in the reverse order to :func:`create`

        :param state: the current state dictionary.  This is the
          `results` dictionary from :func:`create` before this call is
          made.
        :return: None
        """
        return

    def delete(self, state):
        """Cleanup actions

        Actions to taken when ``dib-block-device delete`` is called.
        This is the cleanup path in case of a reported external
        *failure*.  The nodes are called in the reverse order to
        :func:`create`

        :param state: the current state dictionary.  This is the
          `results` dictionary from :func:`create` before this call is
          made.
        :return: None
        """
        return


@six.add_metaclass(abc.ABCMeta)
class PluginBase(object):
    """The base plugin object

    This is the base plugin object.  Plugins are an instantiation of
    this class.  There should be an entry-point (see setup.cfg)
    defined under ``diskimage_builder.block_device.plugin`` for each
    plugin, e.g.

      foo = diskimage_builder.block_device.levelX.foo:Foo

    A configuration entry in the graph config that matches this entry
    point will create an instance of this class, e.g.

    .. code-block:: yaml

       foo:
         name: foo_node
         base: parent_node
         argument_a: bar
         argument_b: baz

    The ``__init__`` function will be passed two arguments:

    ``config``
       The full configuration dictionary for the entry.
       A unique ``name`` entry can be assumed.  In most cases
       a ``base`` entry will be present giving the parent node
       (see :func:`NodeBase.get_edges`).
    ``defaults``
       The global defaults dictionary (see ``--params``)

    ``get_nodes()`` should return the node object(s) created by the
    config for insertion into the final configuration graph.  In the
    simplest case, this is probably a single node created during
    instantiation.  e.g.

    .. code-block:: python

       class Foo(PluginBase):

         def __init__(self, config, defaults):
             super(Foo, self).__init__()
             self.node = FooNode(config.name, ...)

         def get_nodes(self):
             return [self.node]


    Some plugins require more, however.
    """
    def __init__(self):
        pass

    @abc.abstractmethod
    def get_nodes(self):
        """Return nodes created by the plugin

        :returns: a list of :class:`.NodeBase` objects for insertion
          into the graph
        """
        return
