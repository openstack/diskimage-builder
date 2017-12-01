==========
zipl
==========

Zipl is the bootloader for s390x.

This element installs zipl on the base device holding the /boot directory on the system.
It's mandatory for building s390x images. It replaces the `bootloader` element
(which would install grub2 by default).

This element has been tested with `ubuntu` and `ubuntu-minimal` distro.

Arguments
=========

* ``DIB_ZIPL_DEFAULT_CMDLINE`` sets the CMDLINE parameters that
  are appended to the zipl.conf parameter configuration. It defaults to
  'LANG=en_US.UTF-8 console=ttyS0 console=ttyS1'
