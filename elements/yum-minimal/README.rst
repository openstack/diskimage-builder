===========
yum-minimal
===========
Base element for creating minimal yum-based images.

This element is incomplete by itself, you'll want to use the centos-minimal
or fedora-minimal elements to get an actual base image.

Use of this element will require 'yum' and 'yum-utils' to be installed on
Ubuntu and Debian. Nothing additional is needed on Fedora or CentOS.

The `DIB_OFFLINE` or more specific `DIB_YUMCHROOT_USE_CACHE`
variables can be set to prefer the use of a pre-cached root filesystem
tarball.
