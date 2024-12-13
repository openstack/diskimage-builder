==========
bootloader
==========

Installs ``grub[2]`` on boot partition on the system.

Arguments
=========

* ``DIB_GRUB_TIMEOUT`` sets the ``grub`` menu timeout.  It defaults to
  5 seconds.  Set this to 0 (no timeout) for fast boot times.

* ``DIB_GRUB_TIMEOUT_STYLE`` sets the visibility of the ``grub`` menu.
  It defaults to ``menu``. Set this to   ``hidden`` (or ``countdown``
  as an alias) to not display the menu until the timeout is reached at
  which point the default boot entry will be selected.

* ``DIB_BOOTLOADER_DEFAULT_CMDLINE`` sets parameters that are appended
  to the ``GRUB_CMDLINE_LINUX_DEFAULT`` values in ``grub.cfg``
  configuration. It defaults to ``nofb nomodeset gfxpayload=text``.

* ``DIB_BOOTLOADER_USE_SERIAL_CONSOLE`` allows usage of a serial console
  to be disabled in the resulting image by setting to a value of ``False``.

* ``DIB_BOOTLOADER_SERIAL_CONSOLE`` sets the serial device to be
  used as a console. It defaults to ``hvc0`` for PowerPC,
  ``ttyAMA0,115200`` for ARM64, otherwise ``ttyS0,115200``.

* ``DIB_BOOTLOADER_VIRTUAL_TERMINAL`` sets the virtual terminal be
  used as a console. It defaults to ``tty0``. When explicitly set
  to an empty string then no virtual terminal console kernel argument
  is added.

* ``DIB_NO_TIMER_CHECK`` allows the default kernel argument,
  ``no_timer_check`` to be removed from the kernel command line
  when the value is set to ``False``.

* ``DIB_SKIP_GRUB_PACKAGE_INSTALL`` when set to ``True`` will not install any
  grub packages, and will assume all necessary packages are already installed.
