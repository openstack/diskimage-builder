======
debian
======

This element is based on ``debian-minimal`` with ``cloud-init`` and
related tools installed.  This produces something more like a standard
upstream cloud image.

By default this element creates the latest stable release.  The exact
setting can be found in the ``debian-minimal/environment.d`` directory
in the variable ``DIB_RELEASE``.  If a different release of Debian
should be created, the variable ``DIB_RELEASE`` can be set
appropriately.

.. element_deps::
