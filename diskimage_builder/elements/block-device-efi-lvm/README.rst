====================
Block Device EFI LVM
====================

This provides a block-device configuration for the ``vm`` element to
get a disk suitable for EFI booting which uses LVM to define multiple
volumes mounted to /, /tmp, /var, and /home.

Please note that the sizes of the partitions may not
be enough for production usage, they will need to be resized properly after
deployment depending on the available disk size.

Note on x86 this provides the extra `BIOS boot partition
<https://en.wikipedia.org/wiki/BIOS_boot_partition>`__ and a EFI boot
partition for maximum compatability.

This element requires ``dosfstools`` and ``lvm2`` packages to be installed
on the build system.
