==============
centos-minimal
==============
Create a minimal image based on CentOS

Use of this element will require 'yum' and 'yum-utils' to be installed on
Ubuntu and Debian. Nothing additional is needed on Fedora or CentOS.

By default this builds CentOS 7 images.  Set ``DIB_RELEASE`` to ``7``,
``8`` or ``8-stream`` to explicitly select the release.

For CentOS 7, by default, ``DIB_YUM_MINIMAL_CREATE_INTERFACES`` is set
to enable the creation of
``/etc/sysconfig/network-scripts/ifcfg-eth[0|1]`` scripts to enable
DHCP on the ``eth0`` & ``eth1`` interfaces.  If you do not have these
interfaces, or if you are using something else to setup the network
such as cloud-init, glean or network-manager, you would want to set
this to ``0``.  For CentOS 8 and CentOS 8 Stream, this is set to ``0`` by
default as the system uses NetworkManager by default.
