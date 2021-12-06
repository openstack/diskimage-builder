================
Block Device EFI
================

This provides a block-device configuration for the ``vm`` element to
get a single-partition disk suitable for EFI booting.

Note on x86 this provides the extra `BIOS boot partition
<https://en.wikipedia.org/wiki/BIOS_boot_partition>`__ and a EFI boot
partition for maximum compatability.

This element requires ``mkfs.vfat`` command to be available on the build
system, usually included in the dosfstools OS package.
