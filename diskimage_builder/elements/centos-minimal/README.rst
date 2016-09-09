==============
centos-minimal
==============
Create a minimal image based on CentOS 7.

Use of this element will require 'yum' and 'yum-utils' to be installed on
Ubuntu and Debian. Nothing additional is needed on Fedora or CentOS.

The `DIB_OFFLINE` or more specific `DIB_YUMCHROOT_USE_CACHE`
variables can be set to prefer the use of a pre-cached root filesystem
tarball.

By default, `DIB_YUM_MINIMAL_CREATE_INTERFACES` is set to enable the
creation of `/etc/sysconfig/network-scripts/ifcfg-eth[0|1]` scripts to
enable DHCP on the `eth0` & `eth1` interfaces.  If you do not have
these interfaces, or if you are using something else to setup the
network such as cloud-init, glean or network-manager, you would want
to set this to `0`.
