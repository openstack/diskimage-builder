==============
debian-systemd
==============
Debian used `sysvinit` by default till the `wheezy` release. If you
want to use `systemd` instead of the classic sysv init system on
images up to `wheezy`, include this element in your element list.

For `jessie` onwards, this element is redundant, use a regular debian
or `debian-minimal`.

Note that this works with the ``debian`` element, not the
``debian-minimal`` element.

.. element_deps::
