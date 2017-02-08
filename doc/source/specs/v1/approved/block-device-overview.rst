..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==================
Block Device Setup
==================

During the creation of a disk image (e.g. for a VM), there is the need
to create, setup, configure and afterwards detach some kind of storage
where the newly installed OS can be copied to or directly installed
in.

Problem description
===================

Currently dib is somewhat limited when it comes to setting up the
block device: only one partition that can be used for data. LVM,
encryption, multi-device or installation in an already existing block
device is not supported.

In addition there are several places (main, lib, elements) where the
current way of handling the block device is used (spread knowledge and
implementation).

Also it is not possible, to implement the handling as different
elements: it is not possible to pass results of one element in the
same phase to another element.  Passing results from one phase to dib
main is limited.

Use Cases
---------

Possible use cases are (Actor: End User)

#. User wants to use an existing block device to install an system
   image in (like hd, iSCSI, SAN lun, ...).
#. User wants that the system will be installed in multiple
   partitions.
#. User wants that the partitioning is done in a specific way
   (optimize for speed, optimize for size).
#. User wants to use LVM to install the system in (multiple PV, VG and
   LV).
#. User wants to encrypt a partition or a LV where (parts) of the
   system are installed in.
#. User wants specific file systems on specific partitions or LVs.

Please note that these are only examples and details are described and
implemented by different sub-specs.

Proposed change
===============

Because of the current way to execute elements, it is not possible to
have different elements for each feature.  Instead the changes will be
implemented in a python module 'block_device' placed in the
'diskimage_builder' directory.

The entry-point mechanism is used to create callable python programs.
These python programs are directly called from within the dib-main.

There is the need to implement some functions or classes that take
care about common used new functionality: e.g. storing state between
phases, calling python sub-modules and passing arguments around.
These functionality is implemented as needed - therefore it is most
likely that the first patch implements also big parts of these
infrastructure tasks.

Alternatives
------------
#. Rewrite DIB in the way that elements can interchange data, even if
   they are called during one phase.
   This would influence the way all existing elements are called - and
   might lead to unpredictable results.
#. In addition there is the need to introduce at least two additional
   phases: because major parts of the block device handling are
   currently done in main and these must be passed over to elements.
#. Another way would be to implement everything in one element:
   this has the disadvantage, that other elements are not allowed to
   use the 'block_device' phase any longer and also passing around
   configuration and results is still not possible (see [3]).

API impact
----------

Is described in the sub-elements.

Security impact
---------------

Is described in the sub-elements.

Other end user impact
---------------------

Paradigm changes from execute script to configuration for block_device
phase.

Performance Impact
------------------

Is described in the sub-elements.

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  ansreas (andreas@florath.net)

Would be good, if other people would support this - and specify and
implement modules.

Work Items
----------

This is an overview over changes in the block device layer.  Each
level or module needs it's own spec.

A first step is to reimplement the existing functionality, this
contains:

#. Level 0: Local Loop module
   Use loop device on local image file
   (This is already implemented: [1])
#. Level 1: partitioning module
   (This is already implemented: [4])
#. Level 2: Create File System
   An initial module uses ext4 only
#. Level 3: Mounting

As a second step the following functionality can be added:

* Level 1: LVM module
* Level 2: Create File System
  (swap)
* Level 2: Create File System
  (vfat, needed for UEFI)
* Level 2: Create File System
  (xfs)

Of course any other functionality can also be added when needed and wanted.

Dependencies
============

Is described in the sub-elements.

Testing
=======

Is described in the sub-elements.

Documentation Impact
====================

Is described in the sub-elements.

References
==========

[1] Implementation of Level 0: Local Loop module
    https://review.openstack.org/319591
[2] 'Block Device Setup for Disk-Image-Builder'
    https://etherpad.openstack.org/p/C80jjsAs4x
[3] partitioning-parted
    This was a first try to implement everything
    as an element - it shows the limitation.
    https://review.openstack.org/313938
[4] Implementation of Level 1: partitioning module
    https://review.openstack.org/322671
