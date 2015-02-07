=====
uboot
=====
Perform kernel/initrd post-processing for UBoot.

This element helps post-process the kernel/initrd
for use with uboot. It works with ramdisk images
as well as user images.

This element needs u-boot-tools to be installed
on the host.

The load address and entry point for UBoot kernel
can be specified as shown in the example below.

Example:
    export UBOOT\_KERNEL\_ADDR=0x80000
    export UBOOT\_KERNEL\_EP=0x80000
