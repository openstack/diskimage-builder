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
import networkx as nx
import os

from stevedore import extension

from diskimage_builder.block_device.exception import \
    BlockDeviceSetupException
from diskimage_builder.block_device.plugin import NodeBase
from diskimage_builder.block_device.plugin import PluginBase


logger = logging.getLogger(__name__)

_extensions = extension.ExtensionManager(
    namespace='diskimage_builder.block_device.plugin',
    invoke_on_load=False)


# check if a given name is registered as a plugin
def is_a_plugin(name):
    return any(
        _extensions.map(lambda x: x.name == name))


def recurse_config(config, parent_base=None):
    """Convert a config "tree" to it's canonical name/base graph version

    This is a recursive function to convert a YAML layout "tree"
    config into a "flat" graph-based config.

    Arguments:
    :param config: the incoming config dictionary
    :param parent_base: the name of the parent node, if any
    :return: a list of expanded, graph-based config items

    """
    output = []
    this = {}

    # We should only have one key, with multiple values, being the
    # config entries.  e.g. (this was checked by config_tree_to_graph)
    #  mkfs:
    #    type: ext4
    #    label: 1234
    assert len(config.items()) == 1
    for k, v in config.items():
        key = k
        values = v

    # If we don't have a base, we take the parent base; first element
    # can have no base, however.
    if 'base' not in values:
        if parent_base is not None:
            this['base'] = parent_base
    else:
        this['base'] = values['base']

    # If we don't have a name, it is made up as "key_base"
    if 'name' not in values:
        this['name'] = "%s_%s" % (key, this['base'])
    else:
        this['name'] = values['name']

    # Go through the the values dictionary.  Either this is a "plugin"
    # key that needs to be recursed, or it is a value that is part of
    # this config entry.
    for nk, nv in values.items():
        if nk == "partitions":
            # "partitions" is a special key of the "partitioning"
            # object.  It is a list.  Each list-entry gets treated
            # as a top-level entry, so we need to recurse it's
            # keys.  But instead of becoming its own entry in the
            # graph, it gets attached to the .partitions attribute
            # of the parent. (see end for example)
            this['partitions'] = []
            for partition in nv:
                new_part = {}
                for pk, pv in partition.items():
                    if is_a_plugin(pk):
                        output.extend(
                            recurse_config({pk: pv}, partition['name']))
                    else:
                        new_part[pk] = pv
                new_part['base'] = this['base']
                this['partitions'].append(new_part)
        elif is_a_plugin(nk):
            # is this key a plugin directive?  If so, we recurse
            # into it.
            output.extend(recurse_config({nk: nv}, this['name']))
        else:
            # A value entry; just save as part of this entry
            this[nk] = nv

    output.append({k: this})
    return output


def config_tree_to_graph(config):
    """Turn a YAML config into a graph config

    Our YAML config is a list of entries.  Each

    Arguments:
    :parm config: YAML config; either graph or tree
    :return: graph-based result

    """
    output = []

    for entry in config:
        # Top-level entries should be a dictionary and have a plugin
        # registered for it
        if not isinstance(entry, dict):
            raise BlockDeviceSetupException(
                "Config entry not a dict: %s" % entry)

        keys = list(entry.keys())

        if len(keys) != 1:
            raise BlockDeviceSetupException(
                "Config entry top-level should be a single dict: %s" % entry)

        if not is_a_plugin(keys[0]):
            raise BlockDeviceSetupException(
                "Config entry is not a plugin value: %s" % entry)

        output.extend(recurse_config(entry))

    return output


def create_graph(config, default_config, state):
    """Generate configuration digraph

    Generate the configuration digraph from the config

    :param config: graph configuration file
    :param default_config: default parameters (from --params)
    :param state: reference to global state dictionary.
      Passed to :func:`PluginBase.__init__`
    :return: tuple with the graph object (a :class:`nx.Digraph`),
      ordered list of :class:`NodeBase` objects

    """
    # This is the directed graph of nodes: each parse method must
    # add the appropriate nodes and edges.
    dg = nx.DiGraph()

    for config_entry in config:
        # this should have been checked by generate_config
        assert len(config_entry) == 1

        logger.debug("Config entry [%s]", config_entry)
        cfg_obj_name = list(config_entry.keys())[0]
        cfg_obj_val = config_entry[cfg_obj_name]

        # Instantiate a "plugin" object, passing it the
        # configuration entry
        # XXX : would a "factory" pattern for plugins, where we
        # make a method call on an object stevedore has instantiated
        # be better here?
        if not is_a_plugin(cfg_obj_name):
            raise BlockDeviceSetupException(
                ("Config element [%s] is not implemented" % cfg_obj_name))
        plugin = _extensions[cfg_obj_name].plugin
        assert issubclass(plugin, PluginBase)
        cfg_obj = plugin(cfg_obj_val, default_config, state)

        # Ask the plugin for the nodes it would like to insert
        # into the graph.  Some plugins, such as partitioning,
        # return multiple nodes from one config entry.
        nodes = cfg_obj.get_nodes()
        assert isinstance(nodes, list)
        for node in nodes:
            # plugins should return nodes...
            assert isinstance(node, NodeBase)
            # ensure node names are unique.  networkx by default
            # just appends the attribute to the node dict for
            # existing nodes, which is not what we want.
            if node.name in dg.node:
                raise BlockDeviceSetupException(
                    "Duplicate node name: %s" % (node.name))
            logger.debug("Adding %s : %s", node.name, node)
            dg.add_node(node.name, obj=node)

    # Now find edges
    for name, attr in dg.nodes(data=True):
        obj = attr['obj']
        # Unfortunately, we can not determine node edges just from
        # the configuration file.  It's not always simply the
        # "base:" pointer.  So ask nodes for a list of nodes they
        # want to point to.  *mostly* it's just base: ... but
        # mounting is different.
        #  edges_from are the nodes that point to us
        #  edges_to are the nodes we point to
        edges_from, edges_to = obj.get_edges()
        logger.debug("Edges for %s: f:%s t:%s", name,
                     edges_from, edges_to)
        for edge_from in edges_from:
            if edge_from not in dg.node:
                raise BlockDeviceSetupException(
                    "Edge not defined: %s->%s" % (edge_from, name))
            dg.add_edge(edge_from, name)
        for edge_to in edges_to:
            if edge_to not in dg.node:
                raise BlockDeviceSetupException(
                    "Edge not defined: %s->%s" % (name, edge_to))
            dg.add_edge(name, edge_to)

    # this can be quite helpful debugging but needs pydotplus which
    # isn't in requirements.  for debugging, do
    #   .tox/py27/bin/pip install pydotplus
    #   DUMP_CONFIG_GRAPH=1 tox -e py27 -- specific_test
    #   dotty /tmp/graph_dump.dot
    # to see helpful output
    if 'DUMP_CONFIG_GRAPH' in os.environ:
        nx.nx_pydot.write_dot(dg, '/tmp/graph_dump.dot')

    # Topological sort (i.e. create a linear array that satisfies
    # dependencies) and return the object list
    call_order_nodes = nx.topological_sort(dg)
    logger.debug("Call order: %s", list(call_order_nodes))
    call_order = [dg.node[n]['obj'] for n in call_order_nodes]

    return dg, call_order

#
# On partitioning: objects
#
# To be concrete --
#
# partitioning:
#   base: loop0
#   name: mbr
#   partitions:
#     - name: partition1
#       foo: bar
#       mkfs:
#         type: xfs
#         mount:
#           mount_point: /
#
# gets turned into the following graph:
#
# partitioning:
#   partitions:
#     - name: partition1
#       base: image0
#       foo: bar
#
# mkfs:
#   base: partition1
#   name: mkfs_partition1
#   type: xfs
#
# mount:
#   base: mkfs_partition1
#   name: mount_mkfs_partition1
#   mount_point: /
