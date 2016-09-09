==========
bootloader
==========
Installs grub[2] on boot partition on the system. In case GRUB2
is not available in the system, a fallback to Extlinux will happen. It's
also possible to enforce the use of Extlinux by exporting a DIB_EXTLINUX
variable to the environment.
