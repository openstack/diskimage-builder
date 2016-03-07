===========================
cloud-init-disable-resizefs
===========================

The cloud-init resizefs module can be extremely slow and will also
unwittingly create a root filesystem that cannot be booted by grub if
the underlying partition is too big. This removes it from cloud.cfg,
putting the onus for resizing on the user post-boot.
