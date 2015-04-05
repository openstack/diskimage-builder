Installation
============

Diskimage-builder is run directly out of the source repository.

Requirements
------------

If you have 4GB of available physical RAM (As reported by
/proc/meminfo MemTotal), or more, diskimage-builder will create a tmpfs mount
to build the image in. This will improve image build time by building in RAM.
This can be disabled completely by passing --no-tmpfs to disk-image-create.
ramdisk-image-create builds a regular image and then within that does ramdisk
creation. If tmpfs is not used, you will need enough room in /tmp to store two
uncompressed cloud images. If you do have tmpfs, you will still need /tmp space
for one uncompressed cloud image and about 20% of that for working files.

Installation
------------

* Clone the repository locally, then add bin to your path.

* Make sure you have qemu-img (qemu-utils package on Ubuntu/Debian,
  qemu on Fedora/RHEL/openSUSE) and kpartx installed.
