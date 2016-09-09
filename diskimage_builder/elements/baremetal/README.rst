.. _element-baremetal:

=========
baremetal
=========

This is the baremetal (IE: real hardware) element.

Does the following:

 * extracts the kernel and initial ramdisk of the built image.

Optional parameters:

 * DIB_BAREMETAL_KERNEL_PATTERN and DIB_BAREMETAL_INITRD_PATTERN
   may be supplied to specify which kernel files are preferred; this
   can be of use when using custom kernels that don't fit the
   standard naming patterns. Both variables must be provided in
   order for them to have any effect.
