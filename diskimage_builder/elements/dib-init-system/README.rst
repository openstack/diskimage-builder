===============
dib-init-system
===============

Element that handles aspects of the used target's init system.

Any files placed in a ``init-scripts/INIT_SYSTEM`` directory inside the
element will be copied into the appropriate directory if ``INIT_SYSTEM``
is in use on the host.

Environment Variables
---------------------

DIB_INIT_SYSTEM
  :Description: One of ``upstart``, ``systemd``, ``openrc`` or
    ``sysv`` depending on the init system in use for the target image.
    This should be set automatically by your platform elements.
