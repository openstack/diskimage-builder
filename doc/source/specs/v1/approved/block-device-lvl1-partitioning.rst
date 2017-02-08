..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

========================================
Block Device Setup Level 1: Partitioning
========================================

During the creation of a disk image (e.g. for a VM), there is the need
to create, setup, configure and afterwards detach some kind of storage
where the newly installed OS can be copied to or directly installed
in.

Remark
------

The implementation for this proposed changed already exists, was
discussed and is currently waiting for reviews [1].  To have a
complete overview over the block device setup, this document is
provided.

The dependencies are not implemented as they should be, because

* the spec process is currently in the phase of discussion and not
  finalized [2],
* the implementation was finished and reviewed before the spec process
  was described. [1]

Problem description
===================

When setting up a block device there is the need to partitioning the
block device.

Use Cases
---------

User (Actor: End User) wants to create multiple partitions in multiple
block devices where the new system is installed in.

The user wants to specify if the image should be optimized for speed
or for size.

The user wants the same behavior independently of the current host or
target OS.

Proposed change
===============

Move the partitioning functionality from
`elements/vm/block-device.d/10-partition` to a new block_device
python module: `level1/partitioning.py`.

Instead of using a program or a library, the data is written directly
with the help of python `file.write()` into the disk image.

Alternatives
------------

The existing implementation uses the `parted` program (old versions of
DIB were using `sfdisk`).  The first implementations of this change
used the python-parted library.

All these approaches have a major drawback: they automatically
*optimize* based on information collected on the host system - and not
of the target system.  Therefore the resulting partitioning layout may
lead to a degradation of performance on the target system.  A change
in these external programs and libraries also lead to errors during a
DIB run [4] or there are general issues [7].

Also everything build around GNU parted falls under the GPL2 (not
LGPL2) license - which is incompatible with the currently used Apache
license in diskimage-builder.

API impact
----------

Extends the (optional) environment variable
``DIB_BLOCK_DEVICE_CONFIG``: a JSON structure to configure the
(complete) block device setup.  For this proposal the second entry in
the original list will be used (the first part (as described in [5])
is used by the level 0 modules).

The name of this module is `partitioning` (element[0]). The value
(element[1]) is a dictionary.

For each disk that should be partitioned there exists one entry in the
dictionary.  The key is the name of the disk (see [5] how to specify
names for block device level 0).  The value is a dictionary that
defines the partitioning of each disk.

There are the following key / value pairs to define one disk:

label
   (mandatory) Possible values: 'mbr'
   This uses the Master Boot Record (MBR) layout for the disk.
   (Later on this can be extended, e.g. using GPT).

align
   (optional - default value '1MiB')
   Set the alignment of the partition.  This must be a multiple of the
   block size (i.e. 512 bytes).  The default of 1MiB (~ 2048 * 512
   bytes blocks) is the default for modern systems and known to
   perform well on a wide range of targets [6].  For each partition
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
   the partition can later be referenced, e.g. while creating a
   file system.

flags
   (optional) List of flags for the partition. Default: empty.
   Possible values:

   boot
      Sets the boot flag for the partition

size
   (mandatory) The size of the partition.  The size can either be an
   absolute number using units like `10GiB` or `1.75TB` or relative
   (percentage) numbers: in the later case the size is calculated
   based on the remaining free space.

Example:

.. code-block:: yaml

    ["partitioning",
       {"rootdisk": {
         "label": "mbr",
         "partitions":
            [{"name": "part-01",
              "flags": ["boot"],
              "size": "100%"}]}}]

Security impact
---------------

None - functionality stays the same.

Other end user impact
---------------------

None.

Performance Impact
------------------

Measurements showed there is a performance degradation for the target
system of the partition table is not correctly aligned: writing takes
about three times longer on an incorrect aligned system vs. one that
is correctly aligned.

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  ansreas (andreas@florath.net)

Work Items
----------

None - this is already a small part of a bigger change [1].

Dependencies
============

None.

Testing
=======

The refactoring introduces no new test cases: the functionality is
tested during each existing test building VM images.

Documentation Impact
====================

End user: the additional environment variable is described.

References
==========

[1] Refactor: block-device handling (partitioning)
    https://review.openstack.org/322671

[2] Add specs dir
    https://review.openstack.org/336109

[3] Old implementation using parted-lib
    https://review.openstack.org/#/c/322671/1..7/elements/block-device/pylib/block-device/level1/Partitioning.py

[4] ERROR: embedding is not possible, but this is required
    for cross-disk install
    http://lists.openstack.org/pipermail/openstack-dev/2016-June/097789.html

[5] Refactor: block-device handling (local loop)
    https://review.openstack.org/319591

[6] Proper alignment of partitions on an Advanced Format HDD using Parted
    http://askubuntu.com/questions/201164/proper-alignment-of-partitions-on-an-advanced-format-hdd-using-parted

[7] Red Hat Enterprise Linux 6 - Creating a 7TB Partition Using
    parted Always Shows "The resulting partition is not properly
    aligned for best performance"
    http://h20564.www2.hpe.com/hpsc/doc/public/display?docId=emr_na-c03479326&DocLang=en&docLocale=en_US&jumpid=reg_r11944_uken_c-001_title_r0001

[8] Spec for changing the block device handling
    https://review.openstack.org/336946
