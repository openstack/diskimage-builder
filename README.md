Image building tools for Openstack
==================================

These tools are the components of TripleO
(https://wiki.openstack.org/wiki/TripleO) that are responsible for
building disk images.

This repository has the core functionality for building disk images, file
system images and ramdisk images for use with OpenStack (both virtual and bare
metal). The core functionality includes the various operating system specific
modules for disk/filesystem images, and deployment and hardware inventory
ramdisks.

The TripleO project also develops elements that can be used to deploy
OpenStack itself. These live in the TripleO elements repository
(https://git.openstack.org/cgit/openstack/tripleo-image-elements).

What tools are there?
---------------------

* disk-image-create [-a i386|amd64|armhf] -o filename {element} [{element} ...]
  Create an image of element {element}, optionally mixing in other elements.
  Element dependencies are automatically included. Support for other
  architectures depends on your environment being able to run binaries of that 
  platform. For instance, to enable armhf on Ubuntu install the qemu-user-static
  package.

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

Installation
============

* Clone the repository locally, then add bin to your path.

* Make sure you have qemu-img (qemu-utils package on Ubuntu/Debian,
  qemu on Fedora/RHEL) and kpartx installed.

Invocation
==========

The scripts can generally just be run. Options can be set on the command line
or by exporting variables to override those present in lib/img-defaults. -h to
get help.
The image building scripts expect to be able to invoke commands with sudo, so if you
want them to run non-interactively, you should either run them as root, with
sudo -E, or allow your build user to run any sudo command without password.

Using the variable ELEMENTS\_PATH will allow to specify multiple elements locations.
It's a colon (:) separated path list, and it will work in a first path/element found,
first served approach. The included elements tree is used when no path is supplied,
and is added to the end of the path if a path is supplied.

Requirements
============

If you have 4GB of available physical RAM\*, or more, diskimage-builder will
create a tmpfs mount to build the image in. This will improve image build time
by building in RAM. This can be disabled completely by passing --no-tmpfs to
disk-image-create. ramdisk-image-create does not use a tmpfs mount. If tmpfs
is not used, you will need enough room in /tmp to store two uncompressed
cloud images. If you do have tmpfs, you will still need /tmp space for one
uncompressed cloud image and about 20% of that for working files.

\* As reported by /proc/meminfo MemTotal

Caches and offline mode
=======================

Since retrieving and transforming operating system image files, git
repositories, Python or Ruby packages, and so on can be a significant overhead,
we cache many of the inputs to the build process in ~/.cache/image-create/. The
writing an element documention describes the interface within
disk-image-builder for caching. When invoking disk-image-builder the --offline
option will instruct disk-image-builder to not refresh cached resources.

Note that we don't maintain operating system package caches, instead depending
on your local infrastructure (e.g. Squid cache, or an APT or Yum proxy) to 
facilitate caching of that layer, so you need to arrange independently for
offline mode.

Base images
-----------

These are cached by the standard elements - ubuntu, fedora.

source-repositories
-------------------

Git repositories and tarballs obtained via the source-repositories element will
be cached.

C and C++ compilation
---------------------

Ccache is configured by the base element. Any compilation that honours ccache
will be cached.

PyPI
----

The pypi element will bind mount a PyPI mirror from the cache dir and configure
pip and easy-install to use it.

Design
======

Images are built using a chroot and bind mounted /proc /sys and /dev. The goal
of the image building process is to produce blank slate machines that have all
the necessary bits to fulfill a specific purpose in the running of an Openstack
cloud: e.g. a nova-compute node. Images produce either a filesystem image with
a label of cloudimg-rootfs, or can be customised to produce whole disk images
(but will still contain a filesystem labelled cloudimg-rootfs). Once the file
system tree is assembled a loopback device with filesystem (or partition table
and file system) is created and the tree copied into it. The file system
created is an ext4 filesystem just large enough to hold the file system tree
and can be resized up to 1PB in size.

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

The goal of the image building tools is to create machine images that contain
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

Conform to the following conventions:

* Use the environment for overridable defaults, prefixing environment variable
  names with "DIB\_". For example: DIB\_MYDEFAULT=${DIB\_MYDEFAULT:-default}
  If you do not use the DIB\_ prefix you may find that your overrides are
  discarded as the build environment is sanitised.

* Consider that your element co-exists with many others and try to guard
  against undefined behaviours. Some examples:

  * Two elements use the source-repositories element, but use the same filename
    for the source-repositories config file. Files such as these (and indeed the
    scripts in the various .d directories listed below) should be named such
    that they are unique. If they are not unique, when the combined tree is
    created by disk-image-builder for injecting into the build environment, one
    of the files will be overwritten.

  * Two elements copy different scripts into /usr/local/bin with the same name.
    If they both use set -e and cp -n then the conflict will be caught and cause
    the build to fail.

* If your element mounts anything into the image build tree ($TMP\_BUILD\_DIR)
  then it will be automatically unmounted when the build tree is unmounted -
  and not remounted into the filesystem image - if the mount point is needed
  again, your element will need to remount it at that point.

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

 * inputs: $ARCH=i386|amd64|armhf $TARGET\_ROOT=/path/to/target/workarea

* finalise.d: Perform final tuning of the root filesystem. Runs in a chroot
  after the root filesystem content has been copied into the mounted
  filesystem: this is an appropriate place to reset SELinux metadata, install
  grub bootloaders and so on. Because this happens inside the final image, it
  is important to limit operations here to only those necessary to affect the
  filesystem metadata and image itself. For most operations, post-install.d
  is preferred.

* cleanup.d: Perform cleanup of the root filesystem content. For
  instance, temporary settings to use the image build environment HTTP proxy
  are removed here in the dpkg element. Runs outside the chroot on the host
  environment.

 * inputs: $ARCH=i386|amd64|armhf $TARGET\_ROOT=/path/to/target/workarea

* block-device.d: customise the block device that the image will be made on
  (e.g. to make partitions). Runs outside the chroot, after the target tree
  has been fully populated but before the cleanup hook runs.

 * outputs: $IMAGE\_BLOCK\_DEVICE={path}
 * inputs: $IMAGE\_BLOCK\_DEVICE={path} $TARGET\_ROOT={path}

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

* post-install.d: Run code in the chroot. This is a good place to perform
  tasks you want to handle after the OS/application install but before the
  first boot of the image. Some examples of use would be: Run chkconfig
  to disable unneeded services and clean the cache left by the package
  manager to reduce the size of the image.

* first-boot.d: Runs inside the image before rc.local. Scripts from here are
  good for doing per-instance configuration based on cloud metadata.

* environment.d: Bash script snippets that are sourced before running scripts
  in each phase. Use this to set an environment variable for other hooks.

* element-deps : A plain text, newline separated list of elements which will
  be added to the list of elements built into the image at image creation time.

Ramdisk elements support the following files in their element directories:

* binary-deps.d : text files listing executables required to be fed into the 
  ramdisk. These need to be present in $PATH in the build chroot (i.e. need to
  be installed by your elements as described above).

* init.d : POSIX shell script fragments that will be appended to the default
  script executed as the ramdisk is booted (/init).

* udev.d : udev rules files that will be copied into the ramdisk.

Global image-build variables
----------------------------

* DIB\_OFFLINE : this is always set. When not empty, any operations that
  perform remote data access should avoid it if possible. If not possible
  the operation should still be attempted as the user may have an external
  cache able to keep the operation functional.

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
            source-repository-nova - register a source repository
            pre-install.d/
               50-my-ppa           - add a PPA
            install.d/
               10-user             - common Nova user accts
               50-my-pack          - install packages from my PPA
               60-nova             - install nova and some dependencies
            first-boot.d/
               60-nova             - do some post-install config for nova

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

- diskimage-builder has the ability to retrieve source code for an element and
  place it into a directory on the target image during the extra-data phase. The
  default location/branch can then be overridden by the process running
  diskimage-builder, making it possible to use the same element to track more
  then one branch of a git repository or to get source for a local cache. See
  elements/source-repositories/README.md for more information.

Debugging elements
------------------

The build-time environment and command line arguments are captured by the
'base' element and written to /etc/dib\_environment and /etc/dib\_arguments
inside the image.

Export 'break' to drop to a shell during the image build. Break points can be
set either before or after any of the hook points by exporting
"break=[before|after]-hook-name". Multiple break points can be specified as a
comma-delimited string. Some examples:

* break=before-block-device-size will break before the block device size hooks
  are called.

* break=after-first-boot,before-pre-install will break after the first-boot
  hooks and before the pre-install hooks.

* break=after-error will break after an error during a in target hookpoint.

Images are built such that the Linux kernel is instructed not to switch into
graphical consoles (i.e. it will not activate KMS). This maximises
compatibility with remote console interception hardware, such as HP's iLO.
However, you will typicallly only see kernel messages on the console - init
daemons (e.g. upstart) will usually be instructed to output to a serial
console so nova's console-log command can function. There is an element in the
tripleo-image-elements repository called "remove-serial-console" which will
force all boot messages to appear on the main console.

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
