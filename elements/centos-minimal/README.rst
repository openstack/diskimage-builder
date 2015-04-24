==============
centos-minimal
==============
Create a minimal image based on CentOS 7.

Use of this element will require 'yum' and 'yum-utils' to be installed on
Ubuntu and Debian. Nothing additional is needed on Fedora or CentOS.

This element cannot be used with the base element, therefore must pass the -n
flag to disk-image-create when using this element.

The `DIB_OFFLINE` or more specific `DIB_YUMCHROOT_USE_CACHE`
variables can be set to prefer the use of a pre-cached root filesystem
tarball.
