===================
cloud-init-growpart
===================

This element enables growpart for OS images. It allows to grow
Specific partitions during the deployment process.
To enable this element simply include it in the elements list.

**Disclaimer:** This element might not work with some device names supplied, for example when server is deployed and the image is written to a fibre channel device, or a SAS/SATA SSD controller.

* ``DIB_CLOUD_INIT_GROWPART_DEVICES``: List of partition names that needs to be populated in order to be grown by cloud-init. **Populating this variable is mandatory.**
  Cloud-init growpart module documentation - https://cloudinit.readthedocs.io/en/latest/topics/modules.html?highlight=growpart#growpart::

    DIB_CLOUD_INIT_GROWPART_DEVICES:
        - /dev/sda1
        - /dev/vda3


Dependencies:

* ``/usr/bin/growpart``: **is needed on the system in order to grow the partition**,
  however it is part of different packages depending on linux family. That is already taken care of by package-installs.
