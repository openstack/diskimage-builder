==========
bootloader
==========

Installs ``grub[2]`` on boot partition on the system. In case GRUB2 is
not available in the system, a fallback to Extlinux will happen. It's
also possible to enforce the use of Extlinux by exporting a
``DIB_EXTLINUX`` variable to the environment.

Arguments
=========

* ``DIB_GRUB_TIMEOUT`` sets the ``grub`` menu timeout.  It defaults to
  5 seconds.  Set this to 0 (no timeout) for fast boot times.

* ``DIB_BOOTLOADER_DEFAULT_CMDLINE`` sets the CMDLINE parameters that
  are appended to the grub.cfg configuration. It defaults to
  'nofb nomodeset vga=normal'
