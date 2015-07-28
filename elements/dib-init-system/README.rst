===============
dib-init-system
===============

Installs a script (dib-init-system) which outputs the type of init system in
use on the target image. Also sets an environment variable ``DIB_INIT_SYSTEM``
to this value.

Any files placed in a ``init-scripts/INIT_SYSTEM`` directory inside the
element will be copied into the appropriate directory if ``INIT_SYSTEM``
is in use on the host.

Environment Variables
---------------------

DIB_INIT_SYSTEM
  :Description: One of upstart, systemd, or sysv depending on the init system
    in use for the target image.
