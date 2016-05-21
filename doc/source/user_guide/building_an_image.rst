Building An Image
=================

Now that you have diskimage-builder properly :doc:`installed <installation>`
you can get started by building your first disk image.

VM Image
--------

Our first image is going to be a bootable vm image using one of the standard
supported distribution :doc:`elements <../elements>` (Ubuntu or Fedora).

The following command will start our image build (distro must be either
'ubuntu' or 'fedora'):

::

    disk-image-create <distro> vm

This will create a qcow2 file 'image.qcow2' which can then be booted.

Elements
--------

It is important to note that we are passing in a list of
:doc:`elements <../elements>` to disk-image-create in our above command. Elements
are how we decide what goes into our image and what modifications will be
performed.

Some elements provide a root filesystem, such as the ubuntu or fedora element
in our example above, which other elements modify to create our image. At least
one of these 'distro elements' must be specified when performing an image
build. It's worth pointing out that there are many distro elements (you can even
create your own), and even multiples for some of the distros. This is because
there are often multiple ways to install a distro which are very different.
For example: One distro element might use a cloud image while another uses
a package installation tool to build a root filesystem for the same distro.

Other elements modify our image in some way. The 'vm' element in our example
above ensures that our image has a bootloader properly installed. This is only
needed for certain use cases and certain output formats and therefore it is
not performed by default.

Output Formats
--------------

By default a qcow2 image is created by the disk-image-create command. Other
output formats may be specified using the `-t <format>` argument. Multiple
output formats can also be specified by comma separation. The supported output
formats are:

 * qcow2
 * tar
 * vhd
 * docker
 * raw

Disk Image Layout
-----------------

When generating a block image (e.g. qcow2 or raw), by default one
image with one partition holding all files is created.

The appropriate functionality to use multiple partitions and even LVMs
is currently under development; therefore the possible configuration
is currently limited, but will get more flexible as soon as all the
functionality is implemented.

The configuration is done by means of the environment variable
`DIB_BLOCK_DEVICE_CONFIG`.  This variable must hold JSON structured
configuration data.

In future this will be a list of four elements, each describing one
level of block device setup - but because currently only the lowest
level is implemented, it contains only the configuration of the first
level of block device setup

The default is:

::

    DIB_BLOCK_DEVICE_CONFIG='[
        [["local_loop",
          {"name": "rootdisk"}]]]'

In general each module is configured in the way, that the first
element in the list is the name of the module (e.g.  `local_loop`)
followed by a dictionary of parameters (here `{"name": "rootdisk"}`).

Level 0
+++++++

Module: Local Loop
..................

This module generates a local image file and uses the loop device to
create a block device from it.  The symbolic name for this module is
`local_loop`.

Configuration options:

name
  (mandatory) The name of the image.  This is used as the name for the
  image in the file system and also as a symbolic name to be able to
  reference this image (e.g. to create a partition table on this
  disk).

size
  (optional) The size of the disk. The size can be expressed using
  unit names like TiB (1024^4 bytes) or GB (1000^3 bytes).
  Examples: 2.5GiB, 12KB.
  If the size is not specified here, the size as given to
  disk-image-create (--image-size) or the automatically computed size
  is used.

directory
  (optional) The directory where the image is created.

Example:

::

   DIB_BLOCK_DEVICE_CONFIG='[
        [["local_loop",
          {"name": "rootdisk"}],
         ["local_loop",
          {"name": "datadisk",
           "size": "7.5GiB",
           "directory": "/var/tmp"}]]]'

This creates two image files and uses the loop device to use them as
block devices.  One image file called `rootdisk` is created with
default size in the default temp directory.  The second image has the
size of 7.5GiB and is created in the `/var/tmp` folder.

Please note that due to current implementation restrictions it is only
allowed to specify one local loop image.

Filesystem Caveat
-----------------

By default, disk-image-create uses a 4k byte-to-inode ratio when creating the
filesystem in the image. This allows large 'whole-system' images to utilize
several TB disks without exhausting inodes. In contrast, when creating images
intended for tenant instances, this ratio consumes more disk space than an
end-user would expect (e.g. a 50GB root disk has 47GB avail.). If the image is
intended to run within a tens to hundrededs of gigabyte disk, setting the
byte-to-inode ratio to the ext4 default of 16k will allow for more usable space
on the instance. The default can be overridden by passing --mkfs-options like
this::

    disk-image-create --mkfs-options '-i 16384' <distro> vm

Speedups
--------
If you have 4GB of available physical RAM (as reported by /proc/meminfo
MemTotal), or more, diskimage-builder will create a tmpfs mount to build the
image in. This will improve image build time by building it in RAM.
By default, the tmpfs file system uses 50% of the available RAM.
Therefore, the RAM should be at least the double of the minimum tmpfs
size required.
For larger images, when no sufficient amount of RAM is available, tmpfs
can be disabled completely by passing --no-tmpfs to disk-image-create.
ramdisk-image-create builds a regular image and then within that image
creates ramdisk.
If tmpfs is not used, you will need enough room in /tmp to store two
uncompressed cloud images. If tmpfs is used, you would still need /tmp space
for one uncompressed cloud image and about 20% of that image for working files.

