========================
ubuntu-systemd-container
========================

The ``ubuntu-systemd-container`` element uses debootstrap for generating
a minimal image for use by machine containers. In contrast the ``ubuntu``
element uses the cloud-image as the initial base and the ``ubuntu-minimal``
builds an image to be used for hosts.

By default this element creates the latest LTS release.  The exact
setting can be found in the ``ubuntu-common`` element's ``environment.d``
directory in the variable ``DIB_RELEASE``.  If a different release of
Ubuntu should be created, the variable ``DIB_RELEASE`` can be set
appropriately.

Note that this element installs ``systemd-sysv`` as the init system for
18.04+.

.. element_deps::
