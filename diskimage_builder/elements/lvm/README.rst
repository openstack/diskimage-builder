=====
lvm
=====
This is the LVM support element for Ubuntu Xenial.

Note that this element requires initramfs-tools and lvm2
packages to be added to the DIB image using -p option.
If this is not the case, an error will be triggered.

This element enables that an image build with a customized
DIB_BLOCK_DEVICE_CONFIG containing LVM volumes will boot
properly.

On CentOS like distributions, you should use dracut-regenerate
element instead of current lvm element.
