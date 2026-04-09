==================
systemd-machine-id
==================

Initialises ``/etc/machine-id`` during image build by running
``systemd-machine-id-setup`` in the pre-install phase.

Image-based builds (e.g. from a qcow2 or tarball) may not have a
machine-id present.  One may also be absent when systemd has not yet
been upgraded as part of the build.  Certain kernel install scripts
check for ``/etc/machine-id`` and bail silently when it is missing,
leaving kernel packages installed but without an initramfs or kernel
copied into place.

The machine-id set here is a temporary build-time value.  It is
cleared by the ``sysprep`` element so that each deployed instance
receives a unique id on first boot.
