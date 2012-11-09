Image building tools for Openstack
==================================

These tools are the components of tripleo (https://github.com/tripleo/demo)
that do the plumbing involved in building disk images. Specific configs live
in the demo repository, while the reusable tools live here.

What tools are there?
---------------------

* disk-image-create -o filename {flavour} [{flavour} ...] : Create an image of
  flavour {flavour}, optionally mixing in other flavours.

* ramdisk-image-create -o filename {flavour} [{flavour} ...] : Create a kernel+
  ramdisk pair for running maintenance on bare metal machines (deployment,
  inventory, burnin etc).

    ramdisk-image-create -o deploy.ramdisk deploy

* disk-image-get-kernel filename : Extract the appropriate kernel and ramdisk
  to use when doing PXE boot using filename as the image for a machine.

* flavours can be found in the top level flavours directory.

Why?
----

Automation: While users and operators can manually script or put together ram
disks and disk images, mature automation makes customisation and testing easier.

Design
======

Still brief - more details needed.

Images are built using a chroot and bind mounted /proc /sys and /dev. The goal
of the image building process is to produce blank slate machines that have all
the necessary bits to fulfill a specific purpose in the running of an Openstack
cloud: e.g. a nova-compute node.

A flavour is a particular set of code that alters how the image is built, or
runs within the chroot to prepare the image. E.g. the local-config flavour
copies in the http proxy and ssh keys of the user running the image build
process into the image, whereas the vm flavour makes the image build a regular
VM image with partition table and installed grub boot sector. 

Existing flavours
-----------------

Flavours are found in the subdirectory flavours. Each flavour is in a directory
named after the flavour itself. Flavours *should* have a README.md in the root
of the flavour directory describing what it is for.

Writing a flavour
-----------------

Make as many of the following subdirectories as you need, depending on what
part of the process you need to customise:

* block-device.d: customise the block device that the image will be made on
  (e.g. to make partitions).

 * outputs: $IMAGE\_BLOCK\_DEVICE={path}
 * inputs: $IMAGE\_BLOCK\_DEVICE={path}

* extra-data.d: pull in extra data from the host environment that hooks may
  need during image creation. This should copy any data (such as SSH keys,
  http proxy settings and the like) somewhere under $TMP\_HOOKS\_PATH.

 * outputs: None
 * inputs: $TMP\_HOOKS\_PATH

* pre-install.d: Run code in the chroot before customisation or packages are
  installed. A good place to add apt repositories.

* install.d: Runs after pre-install.d in the chroot. This is a good place to
  install packages, chain into configuration management tools or do other
  image specific operations.

* first-boot.d: Runs inside the image before rc.local. Scripts from here are
  good for doing per-instance configuration based on cloud metadata.

Ramdisk flavours support the following files in their flavour directories:

* binary-deps : executables required to be fed into the ramdisk. These need
  to be present in your $PATH.

* init : a POSIX shell script fragment that will be appended to the default
  script executed as the ramdisk is booted (/init)

Third party flavours
--------------------

Pending implementation. The idea is to have a search path for flavours.

Installation
============

* Clone the repository locally, then add bin to your path.

* Copy sudoers.d/\* into your /etc/sudoers.d/. (Warning, use visudo -c -f
  {filename} to check that each one parses successfully on your machine, so you
  don't break your machine).

Invocation
==========

The scripts can generally just be run. Options can be set on the command line
or by exporting variables to override those present in lib/img-defaults. -h to
get help.
