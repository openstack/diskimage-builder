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
