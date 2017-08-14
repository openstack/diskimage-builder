==============
debian-minimal
==============

The ``debian-minimal`` element uses debootstrap for generating a
minimal image.

By default this element creates the latest stable release.  The exact
setting can be found in the element's ``environment.d`` directory in
the variable ``DIB_RELEASE``.  If a different release of Debian should
be created, the variable ``DIB_RELEASE`` can be set appropriately.

Note that this element installs ``systemd-sysv`` as the init system

.. element_deps::
