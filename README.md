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

Images are built using a chroot and bind mounted /proc /sys and /dev. The goal
of the image building process is to produce blank slate machines that have all
the necessary bits to fulfill a specific purpose in the running of an Openstack
cloud: e.g. a nova-compute node.

A flavour is a particular set of code that alters how the image is built, or
runs within the chroot to prepare the image. E.g. the local-config flavour
copies in the http proxy and ssh keys of the user running the image build
process into the image, whereas the vm flavour makes the image build a regular
VM image with partition table and installed grub boot sector. The mellanox
flavour adds support for mellanox infiniband hardware to both the deploy
ramdisk and the built images.

Images start as a base ubuntu cloud image. Other distributions may be added in
future, the infrastructure deliberately makes few assumptions about the exact
operating system is use. The base image has opensshd running (a new key
generated on first boot) and accepts use keys via the cloud metadata service,
loading them into the 'ubuntu' user.

The goal of a built image is to have any global configuration ready to roll,
but nothing that ties it to a specific cloud instance: images should be able to
be dropped into a test cloud and validated, and then deployed into a production
cloud (usually via bare metal nova) for production use. As such, the image
contents can be modelled as three distinct portions:

- global content: the actual code, kernel, always-applicable config (like
  disabling password authentication to sshd).
- metadata / config management provided configuration: user ssh keys, network
  address and routes, configuration management server location and public key,
  credentials to access other servers in the cloud. These are typically
  refreshed on every boot.
- persistent state: sshd server key, database contents, swift storage areas,
  nova instance disk images, disk image cache. These would typically be stored
  on a dedicated partition and not overwritten when re-deploying the image.

The goal of the image building tools is to create machine images that content
the correct global content and are ready for 'last-mile' configuration by the
nova metadata API, after which a configuration management system can take over
(until the next deploy, when it all starts over from scratch). 

Existing flavours
-----------------

Flavours are found in the subdirectory flavours. Each flavour is in a directory
named after the flavour itself. Flavours *should* have a README.md in the root
of the flavour directory describing what it is for.

Writing a flavour
-----------------

Make as many of the following subdirectories as you need, depending on what
part of the process you need to customise:

* block-device-size.d: Alter the size (in GB) of the disk image. This is useful
  when a particular flavour will require a certain minimum (or maximum) size.
  You can either error and stop the build, or adjust the size to match.
  NB: Due to the current simple implementation, the last output value wins
  so this should be used rarely - only one flavour in a mix can reliably set
  a size.

 * outputs: $IMAGE\_SIZE={size_in_GB}
 * inputs: $IMAGE_SIZE={size_in_GB}

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

Copyright
=========

Copyright 2012 Hewlett-Packard Development Company, L.P.
Copyright (c) 2012 NTT DOCOMO, INC. 

All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
