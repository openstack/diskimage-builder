# Copyright 2017 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from diskimage_builder.block_device.exception \
    import BlockDeviceSetupException
from diskimage_builder.block_device.plugin import NodeBase
from diskimage_builder.block_device.plugin import PluginBase
from diskimage_builder.block_device.utils import exec_sudo


logger = logging.getLogger(__name__)

#
# LVM
# ---
#
# The LVM config has three required keys; pvs, vgs and lvs
#
# lvm:     ->  LVSNode
#   pvs:   ->  PvsNode
#   lvs:   ->  LvsNode
#   vgs:   ->  VgsNode
#
# The LVMPlugin will verify this and build nodes into the
# configuration graph.
#
# As described below, a LVSNode is created for synchronisation
# purposes.  Thus if you had something like two partitions that became
# two physical-volumes (pv1 & pv2), that you then combine into a
# single volume group (vg) and then create several logical volumes
# (lv1, lv2, lv3) your graph would end up looking like:
#
#  partition1     partition2
#      |               |
#      ---> LVSNode <--+
#              |
#       +------+------+
#       v             v
#      pv1           pv2
#       |             |
#       +-->  vg  <---+
#             |
#       +-----+-----+
#       v     v     v
#      lv1   lv2   lv3
#
# After the create() call on the LVSNode object, the entire LVM setup
# would actually be complete.  The other nodes are all just
# place-holders, and are used for further ordering (for example, the
# fs creation & mounting should depend on the logical volume nodes).
# For this reason, their create() calls are blank.  However, for code
# organisational purposes they have a private _create() and _cleanup()
# call that is driven by the LVSNode object.


class PvsNode(NodeBase):
    def __init__(self, name, state, base, options):
        """Physical volume

        This is a placeholder node for the LVM physical volumes.

        Arguments:
        :param name: Name of this node
        :param state: global state pointer
        :param base: Parent partition
        :param options: config options
        """
        super(PvsNode, self).__init__(name, state)
        self.base = base
        self.options = options

    def _create(self):
        # the underlying device path of our parent was previously
        # recorded into the state during blockdev creation; look it
        # up.
        phys_dev = self.state['blockdev'][self.base]['device']

        cmd = ["pvcreate"]
        cmd.append(phys_dev)
        if self.options:
            cmd.extend(self.options)
        logger.debug("Creating pv command [%s]", cmd)
        exec_sudo(cmd)

        # save state
        if 'pvs' not in self.state:
            self.state['pvs'] = {}
        self.state['pvs'][self.name] = {
            'opts': self.options,
            'device': phys_dev
        }

    def get_edges(self):
        # See LVMNode.get_edges() for how this gets connected
        return ([], [])

    def create(self):
        # see notes in LVMNode object
        pass


class VgsNode(NodeBase):
    def __init__(self, name, state, base, options):
        """Volume Group

        This is a placeholder node for a volume group

        Arguments:
        :param name: Name of this node
        :param state: global state pointer
        :param base: Parent :class:`PvsNodes` this volume group exists on
        :param options: extra options passed to the `vgcreate` command
        """
        super(VgsNode, self).__init__(name, state)
        self.base = base
        self.options = options

    def _create(self):
        # The PV's have saved their actual device name into the state
        # during their _create().  Look at our base elements and thus
        # find the underlying device paths in the state.
        pvs_devs = []
        for pv in self.base:
            pvs_dev = self.state['pvs'][pv]['device']
            pvs_devs.append(pvs_dev)

        cmd = ["vgcreate", ]
        cmd.append(self.name)
        cmd.extend(pvs_devs)
        if self.options:
            cmd.extend(self.options)

        logger.debug("Creating vg command [%s]", cmd)
        exec_sudo(cmd)

        # save state
        if 'vgs' not in self.state:
            self.state['vgs'] = {}
        self.state['vgs'][self.name] = {
            'opts': self.options,
            'devices': self.base,
        }

    def _umount(self):
        exec_sudo(['vgchange', '-an', self.name])

    def get_edges(self):
        # self.base is already a list, per the config.  There might be
        # multiple pv parents here.
        edge_from = self.base
        edge_to = []
        return (edge_from, edge_to)

    def create(self):
        # see notes in LVMNode object
        pass


class LvsNode(NodeBase):
    def __init__(self, name, state, base, options, size, extents):
        """Logical Volume

        This is a placeholder node for a logical volume

        Arguments:
        :param name: Name of this node
        :param state: global state pointer
        :param base: the parent volume group
        :param options: options passed to lvcreate
        :param size: size of the LV, in MB (this or extents must be provided)
        :param extents: size of the LV in extents
        """
        super(LvsNode, self).__init__(name, state)
        self.base = base
        self.options = options
        self.size = size
        self.extents = extents

    def _create(self):
        cmd = ["lvcreate", ]
        cmd.extend(['--name', self.name])
        if self.size:
            cmd.extend(['-L', self.size])
        elif self.extents:
            cmd.extend(['-l', self.extents])
        if self.options:
            cmd.extend(self.options)

        cmd.append(self.base)

        logger.debug("Creating lv command [%s]", cmd)
        exec_sudo(cmd)

        # save state
        self.state['blockdev'][self.name] = {
            'vgs': self.base,
            'size': self.size,
            'extents': self.extents,
            'opts': self.options,
            'device': '/dev/mapper/%s-%s' % (self.base, self.name)
        }

    def _umount(self):
        exec_sudo(['lvchange', '-an',
                   '/dev/%s/%s' % (self.base, self.name)])

    def get_edges(self):
        edge_from = [self.base]
        edge_to = []
        return (edge_from, edge_to)

    def create(self):
        # see notes in LVMNode object
        pass


class LVMNode(NodeBase):
    def __init__(self, name, state, pvs, lvs, vgs):
        """LVM Driver Node

        This is the "global" node where all LVM operations are driven
        from.  In the node graph, the LVM physical-volumes depend on
        this node.  This node then depends on the devices that the
        PV's require.  This node incorporates *all* LVM setup;
        i.e. after the create() call here we have created all pv's,
        lv's and vg.  The <Pvs|Lvs|Vgs>Node objects in the graph are
        therefore just dependency place holders whose create() call
        does nothing.

        Arguments:
        :param name: name of this node
        :param state: global state pointer
        :param pvs: A list of :class:`PvsNode` objects
        :param lvs: A list of :class:`LvsNode` objects
        :param vgs: A list of :class:`VgsNode` objects

        """
        super(LVMNode, self).__init__(name, state)
        self.pvs = pvs
        self.lvs = lvs
        self.vgs = vgs

    def get_edges(self):
        # This node requires the physical device(s), which is
        # recorded in the "base" argument of the PV nodes.
        pvs = []
        for pv in self.pvs:
            pvs.append(pv.base)
        edge_from = set(pvs)

        # The PV nodes should then depend on us.  i.e., we just made
        # this node a synchronisation point
        edge_to = [pv.name for pv in self.pvs]

        return (edge_from, edge_to)

    def create(self):
        # Run through pvs->vgs->lvs and create them
        # XXX: we could theoretically get this same info from walking
        # the graph of our children nodes?  Would that be helpful in
        # any way?
        for pvs in self.pvs:
            pvs._create()
        for vgs in self.vgs:
            vgs._create()
        for lvs in self.lvs:
            lvs._create()

    def umount(self):
        for lvs in self.lvs:
            lvs._umount()

        for vgs in self.vgs:
            vgs._umount()

        exec_sudo(['udevadm', 'settle'])

    def cleanup(self):
        # Information about the PV, VG and LV is typically
        # cached in lvmetad. Even after removing PV device and
        # partitions this data is not automatically updated
        # which leads to a couple of problems.
        # the 'pvscan --cache' scans the available disks
        # and updates the cache.
        # This is in cleanup because it must be called after the
        # umount of the containing block device is done, (which should
        # all be done in umount phase).
        try:
            exec_sudo(['pvscan', '--cache'])
        except BlockDeviceSetupException as e:
            logger.info("pvscan call failed [%s]", e.returncode)


class LVMPlugin(PluginBase):

    def _config_error(self, msg):
        raise BlockDeviceSetupException(msg)

    def __init__(self, config, defaults, state):
        """Build LVM nodes

        This reads the "lvm:" config stanza, validates it and produces
        the PV, VG and LV nodes.  These are all synchronised via a
        LVMNode as described above.

        Arguments:
        :param config: "lvm" configuration dictionary
        :param defaults: global defaults dictionary
        :param state: global state reference
        """

        super(LVMPlugin, self).__init__()

        # note lvm: doesn't require a base ... the base is the
        # physical devices the "pvs" nodes are made on.
        if 'name' not in config:
            self._config_error("Lvm config requires 'name'")
        if 'pvs' not in config:
            self._config_error("Lvm config requires a 'pvs'")
        if 'vgs' not in config:
            self._config_error("Lvm config needs 'vgs'")
        if 'lvs' not in config:
            self._config_error("Lvm config needs 'lvs'")

        # create physical volume nodes
        self.pvs = []
        self.pvs_keys = []
        for pvs_cfg in config['pvs']:
            if 'name' not in pvs_cfg:
                self._config_error("Missing 'name' in pvs config")
            if 'base' not in pvs_cfg:
                self._config_error("Missing 'base' in pvs_config")

            pvs_item = PvsNode(pvs_cfg['name'], state,
                               pvs_cfg['base'],
                               pvs_cfg.get('options'))
            self.pvs.append(pvs_item)

        # create volume group nodes
        self.vgs = []
        self.vgs_keys = []
        for vgs_cfg in config['vgs']:
            if 'name' not in vgs_cfg:
                self._config_error("Missing 'name' in vgs config")
            if 'base' not in vgs_cfg:
                self._config_error("Missing 'base' in vgs config")

            # Ensure we have a valid PVs backing this VG
            for pvs in vgs_cfg['base']:
                if not any(pv.name == pvs for pv in self.pvs):
                    self._config_error("base:%s in vgs does not "
                                       "match a valid pvs" % pvs)
            vgs_item = VgsNode(vgs_cfg['name'], state, vgs_cfg['base'],
                               vgs_cfg.get('options', None))
            self.vgs.append(vgs_item)

        # create logical volume nodes
        self.lvs = []
        for lvs_cfg in config['lvs']:
            if 'name' not in lvs_cfg:
                self._config_error("Missing 'name' in lvs config")
            if 'base' not in lvs_cfg:
                self._config_error("Missing 'base' in lvs config")
            if 'size' not in lvs_cfg and 'extents' not in lvs_cfg:
                self._config_error("Missing 'size' or 'extents' in lvs config")

            # ensure this logical volume has a valid volume group base
            if not any(vg.name == lvs_cfg['base'] for vg in self.vgs):
                self._config_error("base:%s in lvs does not match a valid vg" %
                                   lvs_cfg['base'])

            lvs_item = LvsNode(lvs_cfg['name'], state, lvs_cfg['base'],
                               lvs_cfg.get('options', None),
                               lvs_cfg.get('size', None),
                               lvs_cfg.get('extents', None))
            self.lvs.append(lvs_item)

        # create the "driver" node
        self.lvm_node = LVMNode(config['name'], state,
                                self.pvs, self.lvs, self.vgs)

    def get_nodes(self):
        # the nodes for insertion into the graph are all of the pvs,
        # vgs and lvs nodes we have created above and the root node and
        # the cleanup node.
        return self.pvs + self.vgs + self.lvs \
            + [self.lvm_node]
