================
Block Device GPT
================

This is an override for the default block-device configuration
provided in the ``vm`` element to get a GPT based single-partition
disk, rather than the default MBR.

Note this provides the extra `BIOS boot partition
<https://en.wikipedia.org/wiki/BIOS_boot_partition>`__ as required for
non-EFI boot environments.
