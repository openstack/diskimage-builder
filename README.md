Image building tools for Openstack
==================================

These tools are the components of tripleo (https://github.com/tripleo/incubator)
that do the plumbing involved in building disk images. Specific configs live
in the incubator repository, while the reusable tools live here.

What tools are there?
---------------------

* disk-image-create -o filename {element} [{element} ...] : Create an image of
  element {element}, optionally mixing in other elements. You will usually want
  to include the "base" element in your image.

* ramdisk-image-create -o filename {element} [{element} ...] : Create a kernel+
  ramdisk pair for running maintenance on bare metal machines (deployment,
  inventory, burnin etc).

    ramdisk-image-create -o deploy.ramdisk deploy

* disk-image-get-kernel filename : Extract the appropriate kernel and ramdisk
  to use when doing PXE boot using filename as the image for a machine.

* elements can be found in the top level elements directory.

* element-info : Extract information about elements.

Why?
----

Automation: While users and operators can manually script or put together ram
disks and disk images, mature automation makes customisation and testing easier.

Design
======

Images are built using a chroot and bind mounted /proc /sys and /dev. The goal
of the image building process is to produce blank slate machines that have all
the necessary bits to fulfill a specific purpose in the running of an Openstack
cloud: e.g. a nova-compute node. Images produce either a filesystem image with
a label of cloudimg-rootfs, or can be customised to produce disk images (but
will still contain a filesystem labelled cloudimg-rootfs).

An element is a particular set of code that alters how the image is built, or
runs within the chroot to prepare the image. E.g. the local-config element
copies in the http proxy and ssh keys of the user running the image build
process into the image, whereas the vm element makes the image build a regular
VM image with partition table and installed grub boot sector. The mellanox
element adds support for mellanox infiniband hardware to both the deploy
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

Existing elements
-----------------

Elements are found in the subdirectory elements. Each element is in a directory
named after the element itself. Elements *should* have a README.md in the root
of the element directory describing what it is for.

Writing an element
-----------------

Make as many of the following subdirectories as you need, depending on what
part of the process you need to customise:

* root.d: Create or adapt the initial root filesystem content. This is where
  alternative distribution support is added, or customisations such as
  building on an existing image. If no element configures a root, the ubuntu
  element will be automatically invoked to obtain an Ubuntu image.
  Runs outside the chroot on the host environment.
  
  Only one element can use this at a time unless particular care is taken not
  to blindly overwrite but instead to adapt the context extracted by other
  elements.

 * inputs: $ARCH=i386|amd64 $TARGET\_ROOT=/path/to/target/workarea

* cleanup.d: Perform cleanups of the root filesystem content. For instance,
  temporary settings to use the image build environment HTTP proxy are removed
  here in the dpkg element. Runs outside the chroot on the host environment.

 * inputs: $ARCH=i386|amd64 $TARGET\_ROOT=/path/to/target/workarea

* block-device-size.d: Alter the size (in GB) of the disk image. This is useful
  when a particular element will require a certain minimum (or maximum) size.
  You can either error and stop the build, or adjust the size to match.
  NB: Due to the current simple implementation, the last output value wins
  so this should be used rarely - only one element in a mix can reliably set
  a size.

 * outputs: $IMAGE\_SIZE={size\_in\_GB}
 * inputs: $IMAGE\_SIZE={size\_in\_GB}

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

* element-deps : A plain text, newline separated list of elements which will
  be added to the list of elements built into the image at image creation time.

Ramdisk elements support the following files in their element directories:

* binary-deps : executables required to be fed into the ramdisk. These need
  to be present in your $PATH.

* init : a POSIX shell script fragment that will be appended to the default
  script executed as the ramdisk is booted (/init)

Structure of an element
-----------------------

The above-mentioned global content can be further broken down in a way that
encourages composition of elements and reusability of their components. One
possible approach to this would be to label elements as either a "driver",
"service", or "config" element. Below are some examples.

- Driver-specific elements should only contain the necessary bits for that
  driver:
      elements/
         driver-mellanox/
            init           - modprobe line
            install.d/
               10-mlx      - package installation

- An element that installs and configures Nova might be a bit more complex:
      elements/
         service-nova/
            pre-install.d/
               50-my-ppa   - add a PPA
            install.d/
               10-user     - common Nova user accts
               50-my-pack  - install packages from my PPA
               60-nova     - install nova and some dependencies
            first-boot.d/
               60-nova     - do some post-install config for nova

- In the general case, configuration should probably be handled either by the
  meta-data service (eg, during first-boot.d) or via normal CM tools
  (eg, salt). That being said, it may occasionally be desirable to create a
  set of elements which express a distinct configuration of the same software
  components. For example, if one were to bake a region-specific SSL cert into
  the images deployed in each region, one might express it like this:
      elements/
         config-az1/
            first-boot.d/
               20-ssl      - add the az1 certificate
         config-az2/
            first-boot.d/
               20-ssl      - add the az2 certificate

In this way, depending on the hardware and in which availability zone it is
to be deployed, an image would be composed of:

  zero or more driver-elements
  one or more service-elements
  zero or more config-elements

It should be noted that this is merely a naming convention to assist in
managing elements. Diskimage-builder is not, and should not be, functionally
dependent upon specific element names.

Debugging elements
------------------

Export 'break' to drop to a shell during the image build. Break points can be
set either before or after any of the hook points by exporting
"break=[before|after]-hook-name". Multiple break points can be specified as a
comma-delimited string. Some examples:

* break=before-block-device-size will break before the block device size hooks
  are called.

* break=after-first-boot,before-pre-install will break after the first-boot
  hooks and before the pre-install hooks.

Testing Elements
----------------

Elements can be tested using python. To create a test:

* Create a directory called 'tests' in the element directory.

* Create an empty file called '\_\_init\_\_.py' to make it into a python
  package.

* Create your test files as 'test\_whatever.py', using regular python test
  code.

To run all the tests use testr - `testr run`. To run just some tests provide
one or more regex filters - tests matching any of them are run -
`testr run apt-proxy`.

Third party elements
--------------------

Pending implementation. The idea is to have a search path for elements.

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
