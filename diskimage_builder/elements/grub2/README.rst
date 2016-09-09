=====
grub2
=====
This image installs grub2 bootloader on the image, that's necessary for
the local boot feature in Ironic to work. This is being made a separated
element because usually images have grub2 removed for space reasons and
also because they are going to boot from network (PXE boot).
