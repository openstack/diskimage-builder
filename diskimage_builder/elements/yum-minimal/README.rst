===========
yum-minimal
===========
Base element for creating minimal yum-based images.

This element is incomplete by itself, you'll want to use the centos-minimal
or fedora-minimal elements to get an actual base image.

Use of this element will require 'yum' and 'yum-utils' to be installed on
Ubuntu and Debian. Nothing additional is needed on Fedora or CentOS.

If you wish to have DHCP networking setup for eth0 & eth1 via
/etc/sysconfig/network-config scripts/ifcfg-eth[0|1], set the
environment variable `DIB_YUM_MINIMAL_CREATE_INTERFACES` to `1`.

If you wish to build from specific mirrors, set
``DIB_YUM_MINIMAL_BOOTSTRAP_REPOS`` to a directory with the ``.repo``
files to use during bootstrap and build.  The repo files should be
named with a prefix ``dib-mirror-`` and will be removed from the final
image.
