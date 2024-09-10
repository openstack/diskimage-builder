=================
replace-partition
=================

A standalone element which consumes a base image which was created with
``diskimage-builder`` and rebuilds it without making any packaging changes. This
allows the image contents to be copied to a new block device layout. Use cases
for this element include:

* Rebuilding a whole-disk image with a different partition layout by setting
  ``DIB_BLOCK_DEVICE_CONFIG``
* Rebuilding a whole-disk image with the same partitions but with the sector
  size increased to 4096 bytes

See element ``replace-partition-redhat`` for a full example of how to use this element

.. WARNING::
   When using this element or elements based upon it, differences in the
   needs of ramdisk component artifacts are generally **not** accounted for.
   I.E. if you rebuild an image which did not have LVM to a disk layout with
   LVM, then the image is *unlikely* to work because the ramdisk lacks the
   contents necessary to detect and initailize the ramdisk.

.. WARNING::
   When rebuilding images, specifically with filesystems like XFS, you should
   utilize diskimage-builder on the same OS and Version as the image you
   are rebuilding. This is because some filesystem version and metadata
   characteristics of newer host kernels can prevent the image from being used
   by the kernel inside of the image. This is most pertinant with the XFS
   filesystem, but there may be other cases we are unaware of.

Arguments
=========

The following arguments are mandatory and should be set to the correct values as
for other distro elements:

* ``DISTRO_NAME``
* ``DIB_RELEASE``
* ``EFI_BOOT_DIR``
* ``DIB_INIT_SYSTEM``
* ``DIB_BLOCK_DEVICE``
* ``DIB_LOCAL_IMAGE``

``DIB_SOURCE_BLOCK_SIZE`` can be set to 4096 if the base image
``DIB_LOCAL_IMAGE`` was created with a 4096 byte sector size.
