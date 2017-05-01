# Copyright 2016-2017 Andreas Florath (andreas@florath.net)
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

import logging

logger = logging.getLogger(__name__)


class TreeConfig(object):
    """Supports simple tree-like configuration

    When using the new (complete) configuration there is a need to
    specify the complete digraph of block level configurations.  This
    provides great flexibility for the cost of complex configurations:
    each and every single element must be completely specified.  In
    many simple use cases the configuration flexibility is not
    needed.

    With the help of this object the simple to use and short tree-like
    configuration is converted automatically into the complete digraph
    configuration which can be used to create the block device
    elements.
    """

    def __init__(self, type_string):
        self.type_string = type_string

    def config_tree_to_digraph(self, config_key, config_value, dconfig,
                               default_base_name, plugin_manager):
        logger.debug("called [%s] [%s] [%s]"
                     % (config_key, config_value, default_base_name))
        base_name = config_value['base'] if 'base' in config_value \
                    else default_base_name
        name = config_value['name'] \
               if 'name' in config_value \
                  else "%s_%s" % (config_key, base_name)
        assert config_key == self.type_string

        nconfig = {'base': base_name, 'name': name}
        for k, v in config_value.items():
            if k not in plugin_manager:
                nconfig[k] = v
            else:
                plugin_manager[k].plugin \
                    .tree_config.config_tree_to_digraph(
                        k, v, dconfig, name, plugin_manager)

        dconfig.append({self.type_string: nconfig})
        logger.debug("finished new [%s] complete [%s]" % (nconfig, dconfig))
