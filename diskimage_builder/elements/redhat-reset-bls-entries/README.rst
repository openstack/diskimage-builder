========================
redhat-reset-bls-entries
========================

Renames Boot Loader Specification (BLS) entries in
``/boot/loader/entries/`` to use the machine-id set during the build,
as a workaround for https://bugzilla.redhat.com/show_bug.cgi?id=2032680.

Upstream qcow2 images for CentOS 9-stream and RHEL 9 ship with
pre-existing BLS entries named after the image's original machine-id.
When diskimage-builder sets a new machine-id via ``systemd-machine-id-setup``
(see the ``systemd-machine-id`` element), these entries are stale and
``grub2-mkconfig`` will not update them correctly.  This element renames
each ``*.conf`` entry under ``/boot/loader/entries/`` to match the
build-time machine-id so that subsequent bootloader configuration steps
work as expected.

This element is a no-op on releases other than ``9-stream`` (CentOS)
and ``9`` (RHEL).

This element is pulled in automatically by the ``centos`` and ``rhel``
elements.
