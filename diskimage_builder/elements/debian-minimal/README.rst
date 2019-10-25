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

The element obeys the ``DIB_DISTRIBUTION_MIRROR`` argument for
mirroring (see ``debootsrap`` element documentation).  However, the
security repositories are separate for Debian, so we can not assume
they exist at ``DIB_DISTRIBUTION_MIRROR``.  If you do not wish to use
the upstream repository (from ``security.debian.org``) override it
with ``DIB_DEBIAN_SECURITY_MIRROR``. The security suite name's subpath
can also be overridden to something other than ``/updates`` with the
``DIB_DEBIAN_SECURITY_SUBPATH`` variable.

.. element_deps::
