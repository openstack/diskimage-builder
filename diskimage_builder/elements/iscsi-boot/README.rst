==========
iscsi-boot
==========
Handles configuration for the disk to be capable of serving as
a remote root filesystem through iSCSI. Currently, this element
can configure Ubuntu/Debian images and CentOS7 images.

It performs the following actions:

For Ubuntu/Debian images:
  * Installs the ``open-iscsi`` package.
  * Creates the ``etc/iscsi/iscsi.initramfs`` configuration file and sets
    ``ISCSI_AUTO=true`` within it.
  * Updates the initramfs to apply the changes.

For CentOS7 images:
  * Required ``dracut-regenerate`` element when performs ``disk-image-create``.
  * Updates ``network`` and ``iscsi`` into ``dracut-regenerate`` during
    pre-installs.
  * Updates ``GRUB_CMDLINE_LINUX_DEFAULT`` into ``/etc/default/grub``.
