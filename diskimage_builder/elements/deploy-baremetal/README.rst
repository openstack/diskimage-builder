================
deploy-baremetal
================
A ramdisk that will expose the machine primary disk over iSCSI and reboot
once baremetal-deploy-helper signals it is finished.

.. Warning::

   Ironic has not supported this style of deployment element since it's
   early days. Please consult `ironic-python-agent-builder <https://docs.openstack.org/ironic-python-agent-builder>`_.
