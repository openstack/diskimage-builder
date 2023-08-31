deploy-targetcli
================

Use targetcli for the deploy ramdisk for iSCSI deployments.

.. Warning::
   Ironic has removed the iSCSI deployment interface, it was last available
   in Wallaby, and even then had to be launched by the ironic-python-agent.
   This element is from the early days of baremetal deployment and is
   deprecated.

Provides the necessary scripts and dependencies to use targetcli
for exporting the iscsi target in the deploy ramdisk.

Implemented as a dracut module, so will only work with dracut-based
ramdisks.
