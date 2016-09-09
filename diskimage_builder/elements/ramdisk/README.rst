=======
ramdisk
=======
This is the ramdisk element.

Almost any user building a ramdisk will want to include this in their build,
as it triggers many of the vital functionality from the basic diskimage-builder
libraries (such as init script aggregation, busybox population, etc).

An example of when one might want to use this toolchain to build a ramdisk would
be the initial deployment of baremetal nodes in a TripleO setup. Various tools
and scripts need to be injected into a ramdisk that will fetch and apply a
machine image to local disks. That tooling/scripting customisation can be
easily applied in a repeatable and automatable way, using this element.

NOTE: ramdisks require 1GB minimum memory on the machines they are booting.

See the top-level README.md of the project, for more information about the
mechanisms available to a ramdisk element.
