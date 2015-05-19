Installation
============

Diskimage-builder can either be run directly out of the source repository or
installed via pip. If you plan on doing development on diskimage-builder or
the elements then we recommend you run the tool out of the source repository
as this installation requires minimal extra effort and does not require an
extra install step for your changes to take effect.

Once installed, you will be able to `build images <building_an_image>` using
disk-image-create and the elements included in the main diskimage-builder
repository.


Requirements
------------

Most image formats require the qemu-img tool which is provided by the
qemu-utils package on Ubuntu/Debian or the qemu package on
Fedora/RHEL/opensuse.

Some image formats, such as VHD, may require additional tools. Please see
the disk-image-create help output for more information.

Individual elements can also have additional dependencies for the build host.
It is recommended you check the documentation for each element you are using
to determine if there are any additional dependencies.


Source Installation
-------------------

Clone the diskimage-builder and dib-utils repositories locally:

::

    git clone https://git.openstack.org/openstack/diskimage-builder
    git clone https://git.openstack.org/openstack/dib-utils


Add the bin dirs to your path:

::

    export PATH=$PATH:$(pwd)/diskimage-builder/bin:$(pwd)/dib-utils/bin


Pip Installation
----------------

Installing via pip is as simple as:

::

    pip install diskimage-builder


Speedups
--------

If you have 4GB of available physical RAM (As reported by /proc/meminfo
MemTotal), or more, diskimage-builder will create a tmpfs mount to build the
image in. This will improve image build time by building in RAM.
This can be disabled completely by passing --no-tmpfs to disk-image-create.
ramdisk-image-create builds a regular image and then within that does ramdisk
creation. If tmpfs is not used, you will need enough room in /tmp to store two
uncompressed cloud images. If you do have tmpfs, you will still need /tmp space
for one uncompressed cloud image and about 20% of that for working files.

