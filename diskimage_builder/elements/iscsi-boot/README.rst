==========
iscsi-boot
==========
Handles configuration for the disk to be capable of serving as
a remote root filesystem through iSCSI. Currently, this element
only configures Ubuntu/Debian images.

It performs the following actions:

* Installs the ``open-iscsi`` package.
* Creates the ``etc/iscsi/iscsi.initramfs`` configuration file and sets
  ``ISCSI_AUTO=true`` within it.
* Updates the initramfs to apply the changes.
