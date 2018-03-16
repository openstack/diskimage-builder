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
 * tgz
 * squashfs
 * vhd
 * docker
 * raw

Disk Image Layout
-----------------

The disk image layout (like number of images, partitions, LVM, disk
encryption) is something which should be set up during the initial
image build: it is mostly not possible to change these things later
on.

There are currently two defaults:

* When using the ``vm`` element, an element that provides
  ``block-device`` should be included.  Available ``block-device-*``
  elements cover the common case of a single partition that fills up
  the whole disk and used as root device.  Currently there are MBR,
  GPT and EFI versions.  For example, to use a GPT disk you could
  build with ::

    disk-image-create -o output.qcow vm block-device-gpt ubuntu-minimal

* When not using the ``vm`` element a plain filesystem image, without
  any partitioning, is created.

If you wish to customise the top-level ``block-device-default.yaml``
file from one of the ``block-device-*`` elements, set the environment
variable `DIB_BLOCK_DEVICE_CONFIG`.  This variable must hold YAML
structured configuration data or be a ``file://`` URL reference to a
on-disk configuration file.

There are a lot of different options for the different levels.  The
following sections describe each level in detail.

General Remarks
+++++++++++++++

In general each module that depends on another module has a `base`
element that points to the depending base.  Also each module has a
`name` that can be used to reference the module.

Tree-Like vs. Complete Digraph Configuration
++++++++++++++++++++++++++++++++++++++++++++

The configuration is specified as a digraph_.  Each module is a
node; a edge is the relation of the current element to its `base`.

Because the general digraph_ approach is somewhat complex when it comes
to write it down, the configuration can also be given as a tree_.

.. _digraph: https://en.wikipedia.org/wiki/Directed_graph
.. _tree: https://en.wikipedia.org/wiki/Tree_(graph_theory)

Example: The tree like notation

.. code-block:: yaml

   mkfs:
     name: root_fs
     base: root_part
     mount:
       mount_point: /

is exactly the same as writing

.. code-block:: yaml

   mkfs:
     name: root_fs
     base: root_part

   mount:
     name: mount_root_fs
     base: root_fs
     mount_point: /

Non existing `name` and `base` entries in the tree notation are
automatically generated: the `name` is the name of the base module
prepended by the type-name of the module itself; the `base` element is
automatically set to the parent node in the tree.

In mostly all cases the much simpler tree notation can be used.
Nevertheless there are some use cases when the more general digraph
notation is needed.  Example: when there is the need to combine two or
more modules into one new, like combining a couple of physical volumes
into one volume group.

Tree and digraph notations can be mixed as needed in a configuration.


Limitations
+++++++++++

To provide an interface towards the existing elements, there are
currently three fixed keys used - which are not configurable:

* `root-label`: this is the label of the block device that is mounted at
  `/`.
* `image-block-partition`: if there is a block device with the name
  `root` this is used else the block device with the name `image0` is
  used.
* `image-path`: the path of the image that contains the root file
  system is taken from the `image0`.


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

.. code-block:: yaml

        local_loop:
          name: image0

        local_loop:
          name: data_image
          size: 7.5GiB
          directory: /var/tmp

This creates two image files and uses the loop device to use them as
block devices.  One image file called `image0` is created with
default size in the default temp directory.  The second image has the
size of 7.5GiB and is created in the `/var/tmp` folder.


Level 1
+++++++

Module: Partitioning
....................

This module generates partitions on existing block devices.  This
means that it is possible to take any kind of block device (e.g. LVM,
encrypted, ...) and create partition information in it.

The symbolic name for this module is `partitioning`.

MBR
***

It is possible to create primary or logical partitions or a mix of
them. The numbering of the primary partitions will start at 1,
e.g. `/dev/vda1`; logical partitions will typically start
with `5`, e.g. `/dev/vda5` for the first partition, `/dev/vda6` for
the second and so on.

The number of logical partitions created by this module is theoretical
unlimited and it was tested with more than 1000 partitions inside one
block device.  Nevertheless the Linux kernel and different tools (like
`parted`, `sfdisk`, `fdisk`) have some default maximum number of
partitions that they can handle.  Please consult the documentation of
the appropriate software you plan to use and adapt the number of
partitions.

Partitions are created in the order they are configured.  Primary
partitions - if needed - must be first in the list.

GPT
***

GPT partitioning requires the ``sgdisk`` tool to be available.

Options
*******

There are the following key / value pairs to define one partition
table:

base
   (mandatory) The base device to create the partitions in.

label
   (mandatory) Possible values: 'mbr', 'gpt'
   Configure use of either the Master Boot Record (MBR) or GUID
   Partition Table (GPT) formats

align
   (optional - default value '1MiB'; MBR only)
   Set the alignment of the partition.  This must be a multiple of the
   block size (i.e. 512 bytes).  The default of 1MiB (~ 2048 * 512
   bytes blocks) is the default for modern systems and known to
   perform well on a wide range of targets.  For each partition
   there might be some space that is not used - which is `align` - 512
   bytes.  For the default of 1MiB exactly 1048064 bytes (= 1 MiB -
   512 byte) are not used in the partition itself.  Please note that
   if a boot loader should be written to the disk or partition,
   there is a need for some space.  E.g. grub needs 63 * 512 byte
   blocks between the MBR and the start of the partition data; this
   means when grub will be installed, the `align` must be set at least
   to 64 * 512 byte = 32 KiB.

partitions
   (mandatory) A list of dictionaries. Each dictionary describes one
   partition.

The following key / value pairs can be given for each partition:

name
   (mandatory) The name of the partition.  With the help of this name,
   the partition can later be referenced, e.g. when creating a
   file system.

flags
   (optional) List of flags for the partition. Default: empty.
   Possible values:

   boot (MBR only)
      Sets the boot flag for the partition
   primary (MBR only)
      Partition should be a primary partition. If not set a logical
      partition will be created.

size
   (mandatory) The size of the partition.  The size can either be an
   absolute number using units like `10GiB` or `1.75TB` or relative
   (percentage) numbers: in the later case the size is calculated
   based on the remaining free space.

type (optional)
   The partition type stored in the MBR or GPT partition table entry.

   For MBR the default value is '0x83' (Linux Default partition). Any valid one
   byte hexadecimal value may be specified here.

   For GPT the default value is '8300' (Linux Default partition). Any valid two
   byte hexadecimal value may be specified here. Due to ``sgdisk`` leading '0x'
   should not be used.

Example:

.. code-block:: yaml

   - partitioning:
      base: image0
      label: mbr
      partitions:
        - name: part-01
          flags: [ boot ]
          size: 1GiB
        - name: part-02
          size: 100%

  - partitioning:
      base: data_image
      label: mbr
      partitions:
        - name: data0
          size: 33%
        - name: data1
          size: 50%
        - name: data2
          size: 100%

  - partitioning:
      base: gpt_image
      label: gpt
      partitions:
        - name: ESP
          type: EF00
          size: 16MiB
        - name: data1
          size: 1GiB
        - name: lvmdata
          type: 8E00
          size: 100%

On the `image0` two partitions are created.  The size of the first is
1GiB, the second uses the remaining free space.  On the `data_image`
three partitions are created: all are about 1/3 of the disk size. On
the `gpt_image` three partitions are created: 16MiB one for EFI
bootloader, 1GiB Linux filesystem one and rest of disk will be used
for LVM partition.

Module: LVM
...........

This module generates volumes on existing block devices. This means that it is
possible to take any previous created partition, and create volumes information
in it.

The symbolic name for this module is `lvm`.

There are the following key / value pairs to define one set of volumes:

pvs
    (mandatory) A list of dictionaries. Each dictionary describes one
    physical volume.

vgs
    (mandatory) A list of dictionaries. Each dictionary describes one volume
    group.

lvs
    (mandatory) A list of dictionaries. Each dictionary describes one logical
    volume.

The following key / value pairs can be given for each `pvs`:

name
    (mandatory) The name of the physical volume. With the help of this
    name, the physical volume can later be referenced, e.g. when creating
    a volume group.

base
    (mandatory) The name of the partition where the physical volume
    needs to be created.

options
    (optional) List of options for the physical volume. It can contain
    any option supported by the `pvcreate` command.

The following key / value pairs can be given for each `vgs`:

name
    (mandatory) The name of the volume group. With the help of this name,
    the volume group can later be referenced, e.g. when creating a logical
    volume.

base
    (mandatory) The name(s) of the physical volumes where the volume groups
    needs to be created. As a volume group can be created on one or more
    physical volumes, this needs to be a list.

options
    (optional) List of options for the volume group. It can contain any
    option supported by the `vgcreate` command.

The following key / value pairs can be given for each `lvs`:

name
    (mandatory) The name of the logical volume. With the help of this name,
    the logical volume can later be referenced, e.g. when creating a
    filesystem.

base
    (mandatory) The name of the volume group where the logical volume
    needs to be created.

size
    (optional) The exact size of the volume to be created. It accepts the same
    syntax as the -L flag of the `lvcreate` command.

extents
    (optional) The relative size in extents of the volume to be created. It
    accepts the same syntax as the -l flag of the `lvcreate` command.
    Either size or extents need to be passed on the volume creation.

options
    (optional) List of options for the logical volume. It can contain any
    option supported by the `lvcreate` command.

Example:

.. code-block:: yaml

    - lvm:
        name: lvm
        pvs:
          - name: pv
            options: ["--force"]
            device: root

        vgs:
          - name: vg
            base: ["pv"]
            options: ["--force"]

        lvs:
          - name: lv_root
            base: vg
            size: 1800M

          - name: lv_tmp
            base: vg
            size: 100M

          - name: lv_var
            base: vg
            size: 500M

          - name: lv_log
            base: vg
            size: 100M

          - name: lv_audit
            base: vg
            size: 100M

          - name: lv_home
            base: vg
            size: 200M

On the `root` partition a physical volume is created. On that physical
volume, a volume group is created. On top of this volume group, six logical
volumes are created.

Please note that in order to build images that are bootable using volumes,
your ramdisk image will need to have that support. If the image you are using
does not have it, you can add the needed modules and regenerate it, by
including the `dracut-regenerate` element when building it.


Level 2
+++++++

Module: Mkfs
............

This module creates file systems on the block device given as `base`.
The following key / value pairs can be given:

base
   (mandatory) The name of the block device where the filesystem will
   be created on.

name
   (mandatory) The name of the partition.  This can be used to
   reference (e.g. mounting) the filesystem.

type
   (mandatory) The type of the filesystem, like `ext4` or `xfs`.

label
   (optional - defaults to the name)
   The label of the filesystem.  This can be used e.g. by grub or in
   the fstab.

opts
   (optional - defaults to empty list)
   Options that will passed to the mkfs command.

uuid
   (optional - no default / not used if not givem)
   The UUID of the filesystem.  Not all file systems might
   support this.  Currently there is support for `ext2`, `ext3`,
   `ext4` and `xfs`.

Example:

.. code-block:: yaml

   - mkfs:
       name: mkfs_root
       base: root
       type: ext4
       label: cloudimage-root
       uuid: b733f302-0336-49c0-85f2-38ca109e8bdb
       opts: "-i 16384"


Level 3
+++++++

Module: Mount
.............

This module mounts a filesystem.  The options are:

base
   (mandatory) The name of the filesystem that will be mounted.

name
   (mandatory) The name of the mount point.  This can be used for
   reference the mount (e.g. creating the fstab).

mount_point
   (mandatory) The mount point of the filesystem.

There is no need to list the mount points in the correct order: an
algorithm will automatically detect the mount order.

Example:

.. code-block:: yaml

   - mount:
       name: root_mnt
       base: mkfs_root
       mount_point: /


Level 4
+++++++

Module: fstab
.............

This module creates fstab entries.  The following options exists.  For
details please consult the fstab man page.

base
   (mandatory) The name of the mount point that will be written to
   fstab.

name
   (mandatory) The name of the fstab entry.  This can be used later on
   as reference - and is currently unused.

options
   (optional, defaults to `default`)
   Special mount options can be given.  This is used as the fourth
   field in the fstab entry.

dump-freq
   (optional, defaults to 0 - don't dump)
   This is passed to dump to determine which filesystem should be
   dumped. This is used as the fifth field in the fstab entry.

fsck-passno
   (optional, defaults to 2)
   Determines the order to run fsck.  Please note that this should be
   set to 1 for the root file system. This is used as the sixth field
   in the fstab entry.

Example:

.. code-block:: yaml

   - fstab:
       name: var_log_fstab
       base: var_log_mnt
       options: nodev,nosuid
       dump-freq: 2


Filesystem Caveat
-----------------

By default, disk-image-create uses a 4k byte-to-inode ratio when
creating the filesystem in the image. This allows large 'whole-system'
images to utilize several TB disks without exhausting inodes. In
contrast, when creating images intended for tenant instances, this
ratio consumes more disk space than an end-user would expect (e.g. a
50GB root disk has 47GB avail.). If the image is intended to run
within a tens to hundrededs of gigabyte disk, setting the
byte-to-inode ratio to the ext4 default of 16k will allow for more
usable space on the instance. The default can be overridden by passing
``--mkfs-options`` like this::

    disk-image-create --mkfs-options '-i 16384' <distro> vm

You can also select a different filesystem by setting the ``FS_TYPE``
environment variable.

Note ``--mkfs-options`` are options passed to the mfks *driver*,
rather than ``mkfs`` itself (i.e. after the initial `-t` argument).

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


Chosing an Architecture
-----------------------

If needed you can specify an override the architecture selection by passing a
``-a`` argument like:

::

    disk-image-create -a <arch> ...

Notes about PowerPC Architectures
+++++++++++++++++++++++++++++++++

PowerPC can operate in either Big or Little Endian mode.  ``ppc64``
always refers to Big Endian operation.  When running in little endian
mode it can be referred to as ``ppc64le`` or ``ppc64el``.

Typically ``ppc64el`` refers to a ``.deb`` based distribution
architecture, and ``ppc64le`` refers to a ``.rpm`` based distribution.
Regardless of the distribution the kernel architecture is always
``ppc64le``.

Notes about s390x (z Systems) Architecture
++++++++++++++++++++++++++++++++++++++++++

Images for s390x can only be build on s390x hosts. Trying to build
it with the architecture override on other architecture will
cause the build to fail.

