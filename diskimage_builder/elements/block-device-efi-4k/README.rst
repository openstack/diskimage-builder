================
Block Device EFI
================

This provides a block-device configuration for the ``vm`` element to
get a single-partition disk suitable for EFI booting on a block device
which uses a native 4KiB sector size. This is important because GPT
partitioning relies on sector boundry placement and the GPT disk partition
table always starts on the second sector of the disk.

Note on x86 this provides the extra `BIOS boot partition
<https://en.wikipedia.org/wiki/BIOS_boot_partition>`__ and a EFI boot
partition for maximum compatability.

This element requires ``mkfs.vfat`` command to be available on the build
system, usually included in the dosfstools OS package.

Furthermore, the sector size created by this element will not be compatible
with devices using 512 byte sectors.
