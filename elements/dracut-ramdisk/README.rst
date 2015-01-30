==============
dracut-ramdisk
==============
Build Dracut-based ramdisks

This is an alternative to the `ramdisk` element that uses
Dracut to provide the base system functionality instead of
Busybox.

For elements that need additional drivers in the ramdisk image,
a dracut-drivers.d feature is included that works in a similar
fashion to the binary-deps.d feature.  The element needing to
add drivers should create a dracut-drivers.d directory and
populate it with a single file listing all of the kernel modules
it needs added to the ramdisk.  Comments are not supported in this
file.  Note that these modules must be installed in the chroot first.

By default, the virtio, virtio_net, and virtio_blk modules are
included so that ramdisks are able to function properly in a
virtualized environment.
