Sets up a partitioned disk (rather than building just one filesystem with no
partition table).

By default the disk will have grub[2]-install run on it, in case GRUB2
is not available in the system a fallback to Extlinux will happen. It's
also possible to enforce the use of Extlinux exporting a DIB_EXTLINUX
varible to the environment.
