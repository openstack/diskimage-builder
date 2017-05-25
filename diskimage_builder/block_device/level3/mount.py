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

import logging
import os

from diskimage_builder.block_device.exception \
    import BlockDeviceSetupException
from diskimage_builder.block_device.plugin import NodeBase
from diskimage_builder.block_device.plugin import PluginBase
from diskimage_builder.block_device.utils import exec_sudo
from diskimage_builder.block_device.utils import sort_mount_points


logger = logging.getLogger(__name__)


# There is the need to collect all mount points to be able to
# sort them in a sensible way.
mount_points = {}
# The order of mounting and unmounting is important.
sorted_mount_points = None


class MountPointNode(NodeBase):

    def __init__(self, mount_base, config):
        super(MountPointNode, self).__init__(config['name'])

        # Parameter check
        self.mount_base = mount_base
        for pname in ['base', 'mount_point']:
            if pname not in config:
                raise BlockDeviceSetupException(
                    "MountPoint config needs [%s]" % pname)
            setattr(self, pname, config[pname])
        logger.debug("MountPoint created [%s]" % self)

    def get_node(self):
        global mount_points
        if self.mount_point in mount_points:
            raise BlockDeviceSetupException(
                "Mount point [%s] specified more than once"
                % self.mount_point)
        logger.debug("Insert node [%s]" % self)
        mount_points[self.mount_point] = self
        return self

    def get_edges(self):
        """Insert all edges

        After inserting all the nodes, the order of the mounting and
        umounting can be computed.  There is the need to mount
        mount-points that contain other mount-points first.
        Example: '/var' must be mounted before '/var/log'. If not the
        second is not used for files at all.

        The dependency edge is created in all cases from the base
        element (typically a mkfs) and, if this is not the 'first'
        mount-point, also depend on the mount point before.  This
        ensures that during mounting (and umounting) the correct
        order is used.
        """
        edge_from = []
        edge_to = []
        global mount_points
        global sorted_mount_points
        if sorted_mount_points is None:
            logger.debug("Mount points [%s]" % mount_points)
            sorted_mount_points = sort_mount_points(mount_points.keys())
            logger.info("Sorted mount points [%s]" % (sorted_mount_points))

        # Look for the occurance in the list
        mpi = sorted_mount_points.index(self.mount_point)
        if mpi > 0:
            # If not the first: add also the dependency
            dep = mount_points[sorted_mount_points[mpi - 1]]
            edge_from.append(dep.name)

        edge_from.append(self.base)
        return (edge_from, edge_to)

    def create(self, result, rollback):
        logger.debug("mount called [%s]" % self.mount_point)
        logger.debug("result [%s]" % result)
        rel_mp = self.mount_point if self.mount_point[0] != '/' \
                 else self.mount_point[1:]
        mount_point = os.path.join(self.mount_base, rel_mp)
        if not os.path.exists(mount_point):
            # Need to sudo this because of permissions in the new
            # file system tree.
            exec_sudo(['mkdir', '-p', mount_point])
        logger.info("Mounting [%s] to [%s]" % (self.name, mount_point))
        exec_sudo(["mount", result['filesys'][self.base]['device'],
                   mount_point])

        if 'mount' not in result:
            result['mount'] = {}
        result['mount'][self.mount_point] \
            = {'name': self.name, 'base': self.base, 'path': mount_point}

        if 'mount_order' not in result:
            result['mount_order'] = []
        result['mount_order'].append(self.mount_point)

    def umount(self, state):
        logger.info("Called for [%s]" % self.name)
        exec_sudo(["umount", state['mount'][self.mount_point]['path']])

    def delete(self, state):
        self.umount(state)


class Mount(PluginBase):
    def __init__(self, config, defaults):
        super(Mount, self).__init__()

        self.mount_points = {}

        if 'mount-base' not in defaults:
            raise BlockDeviceSetupException(
                "Mount default config needs 'mount-base'")
        self.mount_base = defaults['mount-base']

        mp = MountPointNode(self.mount_base, config)
        self.mount_points[mp.get_name()] = mp

    def get_nodes(self):
        global sorted_mount_points
        assert sorted_mount_points is None
        nodes = []
        for _, mp in self.mount_points.items():
            nodes.append(mp.get_node())
        return nodes
