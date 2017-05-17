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

from stevedore import extension

from diskimage_builder.block_device.exception import \
    BlockDeviceSetupException


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
