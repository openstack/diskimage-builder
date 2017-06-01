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


logger = logging.getLogger(__name__)


# The order of mounting and unmounting is important.
sorted_mount_points = []


class MountPointNode(NodeBase):

    def __init__(self, mount_base, config, state):
        super(MountPointNode, self).__init__(config['name'], state)

        # Parameter check
        self.mount_base = mount_base
        for pname in ['base', 'mount_point']:
            if pname not in config:
                raise BlockDeviceSetupException(
                    "MountPoint config needs [%s]" % pname)
            setattr(self, pname, config[pname])
        logger.debug("MountPoint created [%s]", self)

    def __lt__(self, other):
        # in words: if the other mount-point has us as it's
        # parent, we come before it (less than it).  e.g.
        #  /var < /var/log < /var/log/foo
        return other.mount_point.startswith(self.mount_point)

    def get_edges(self):
        """Insert all edges

        The dependency edge is created in all cases from the base
        element (typically a mkfs) and, if this is not the 'first'
        mount-point, an edge is created from the mount-point before in
        "sorted order" (see :func:`sort_mount_points`).  This ensures
        that during mounting (and umounting) the globally correct
        order is used.
        """
        edge_from = []
        edge_to = []

        # If we are not first, add our parent in the global dependency
        # list
        mpi = sorted_mount_points.index(self)
        if mpi > 0:
            dep = sorted_mount_points[mpi - 1]
            edge_from.append(dep.name)

        edge_from.append(self.base)
        return (edge_from, edge_to)

    def create(self, rollback):
        logger.debug("mount called [%s]", self.mount_point)
        rel_mp = self.mount_point if self.mount_point[0] != '/' \
                 else self.mount_point[1:]
        mount_point = os.path.join(self.mount_base, rel_mp)
        if not os.path.exists(mount_point):
            # Need to sudo this because of permissions in the new
            # file system tree.
            exec_sudo(['mkdir', '-p', mount_point])
        logger.info("Mounting [%s] to [%s]", self.name, mount_point)
        exec_sudo(["mount", self.state['filesys'][self.base]['device'],
                   mount_point])

        if 'mount' not in self.state:
            self.state['mount'] = {}
        self.state['mount'][self.mount_point] \
            = {'name': self.name, 'base': self.base, 'path': mount_point}

        if 'mount_order' not in self.state:
            self.state['mount_order'] = []
        self.state['mount_order'].append(self.mount_point)

    def umount(self):
        logger.info("Called for [%s]", self.name)
        exec_sudo(["umount", self.state['mount'][self.mount_point]['path']])

    def delete(self):
        self.umount()


class Mount(PluginBase):
    def __init__(self, config, defaults, state):
        super(Mount, self).__init__()

        if 'mount-base' not in defaults:
            raise BlockDeviceSetupException(
                "Mount default config needs 'mount-base'")
        self.node = MountPointNode(defaults['mount-base'], config, state)

        # save this new node to the global mount-point list and
        # re-order it.
        global sorted_mount_points
        mount_points = [x.mount_point for x in sorted_mount_points]
        if self.node.mount_point in mount_points:
            raise BlockDeviceSetupException(
                "Mount point [%s] specified more than once"
                % self.node.mount_point)
        sorted_mount_points.append(self.node)
        sorted_mount_points.sort()
        logger.debug("Ordered mounts now: %s", sorted_mount_points)

    def get_nodes(self):
        return [self.node]
