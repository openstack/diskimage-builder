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

from diskimage_builder.block_device.blockdevice \
    import BlockDeviceSetupException
from diskimage_builder.block_device.tree_config import TreeConfig
from diskimage_builder.block_device.utils import exec_sudo
from diskimage_builder.block_device.utils import sort_mount_points
from diskimage_builder.graph.digraph import Digraph


logger = logging.getLogger(__name__)


# There is the need to collect all mount points to be able to
# sort them in a sensible way.
mount_points = {}
# The order of mounting and unmounting is important.
sorted_mount_points = None


class MountPoint(Digraph.Node):

    @staticmethod
    def _config_error(msg):
        logger.error(msg)
        raise BlockDeviceSetupException(msg)

    def __init__(self, mount_base, config):
        # Parameter check
        self.mount_base = mount_base
        for pname in ['base', 'name', 'mount_point']:
            if pname not in config:
                self._config_error("MountPoint config needs [%s]" % pname)
            setattr(self, pname, config[pname])
        Digraph.Node.__init__(self, self.name)
        logger.debug("MountPoint created [%s]" % self)

    def __repr__(self):
        return "<MountPoint base [%s] name [%s] mount_point [%s]>" \
            % (self.base, self.name, self.mount_point)

    def insert_node(self, dg):
        global mount_points
        if self.mount_point in mount_points:
            self._config_error("Mount point [%s] specified more than once"
                               % self.mount_point)
        logger.debug("Insert node [%s]" % self)
        mount_points[self.mount_point] = self
        dg.add_node(self)

    def insert_edges(self, dg):
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
        logger.debug("Insert edge [%s]" % self)
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
            dg.create_edge(mount_points[sorted_mount_points[mpi - 1]], self)

        bnode = dg.find(self.base)
        assert bnode is not None
        dg.create_edge(bnode, self)

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

    def cleanup(self, state):
        """Mount does not need any cleanup."""
        pass

    def delete(self, state):
        self.umount(state)


class Mount(object):

    type_string = "mount"
    tree_config = TreeConfig("mount")

    def _config_error(self, msg):
        logger.error(msg)
        raise BlockDeviceSetupException(msg)

    def __init__(self, config, params):
        logger.debug("Mounting object; config [%s]" % config)
        self.config = config
        self.params = params

        if 'mount-base' not in self.params:
            MountPoint._config_error("Mount default config needs 'mount-base'")
        self.mount_base = self.params['mount-base']

        self.mount_points = {}

        mp = MountPoint(self.mount_base, self.config)
        self.mount_points[mp.get_name()] = mp

    def insert_nodes(self, dg):
        global sorted_mount_points
        assert sorted_mount_points is None
        for _, mp in self.mount_points.items():
            mp.insert_node(dg)
