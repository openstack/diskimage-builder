========
growvols
========

Grow one or more LVM volumes on first boot.

This installs utility `growvols` which grows the logical volumes in an LVM group
to take available device space.

The positional arguments specify how available space is allocated. They
have the format <volume>=<amount><unit> where:

<volume> is the label or the mountpoint of the logical volume
<amount> is an integer growth amount in the specified unit
<unit> is one of the supported units

Supported units are:

% percentage of available device space before any changes are made
MiB mebibyte (1048576 bytes)
GiB gibibyte (1073741824 bytes)
MB megabyte (1000000 bytes)
GB gigabyte (1000000000 bytes)

Each argument is processed in order and the requested amount is allocated
to each volume until the disk is full. This means that if space is
overallocated, the last volumes may only grow by the remaining space, or
not grow at all, and a warning will be printed. When space is underallocated
the remaining space will be given to the root volume (mounted at /).

The currently supported partition layout is:
- Exactly one of the partitions containing an LVM group
- The disk having unpartitioned space to grow with
- The LVM logical volumes being formatted with XFS filesystems

Example usage:

growvols /var=80% /home=20GB

growvols --device sda --group vg img-rootfs=20% fs_home=20GiB fs_var=60%

Environment variables can be set during image build to enable a systemd unit
which will run growvols on boot:

# DIB_GROWVOLS_TRIGGER defaults to 'manual'. When set to 'systemd' a systemd
# unit will run using the following arguments
export DIB_GROWVOLS_TRIGGER=systemd

# DIB_GROWVOLS_ARGS contains the positional arguments for which volumes to grow
# by what amount. If omitted the volume mounted at / will grow by all available
# space
export DIB_GROWVOLS_ARGS="img-rootfs=20% fs_home=20GiB fs_var=60%"

# DIB_GROWVOLS_GROUP contains the name of the LVM group to extend. Defaults the
# discovered group if only one exists.
export DIB_GROWVOLS_GROUP=vg

# DIB_GROWVOLS_DEVICE is the name of the disk block device to grow the
# volumes in (such as "sda"). Defaults to the disk containing the root mount.
export DIB_GROWVOLS_DEVICE=sda
