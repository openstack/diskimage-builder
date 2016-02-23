#!/bin/bash

# unit testing for some of the common-functions
#
# This is fairly invasive and *may* leave behind mounts, etc, that
# need a human in the loop.  Thus it's mostly useful for developers
# during testing, but not so great for CI

source ../lib/common-functions

#
# Directory mounting and unmounting
#

# make mount points
TMP_DIR=$(mktemp -d)
cd $TMP_DIR
mkdir mnt
mkdir mnt/proc mnt/dev mnt/dev/pts mnt/sysfs mnt/sys

# for extra complexity, simulate the path being behind a symlink
ln -s mnt mnt-symlink
TMP_MOUNT_PATH=$TMP_DIR/mnt-symlink

# mount devices
mount_proc_dev_sys

if [ $(grep "$TMP_DIR" /proc/mounts | wc -l) -ne 4 ]; then
    echo "*** FAILED to mount all directories"
    # we might be in an unclean state here, but something is broken...
    # we don't want to delete mounted system directories
    return 1
else
    echo "*** PASS : mounted all directories"
fi

# umount devices
unmount_dir $TMP_MOUNT_PATH

if grep -q "$TMP_DIR" /proc/mounts; then
    echo "*** FAILED due to mounts being left behind"
    return 1
else
    echo "*** PASS all directories unmounted"
fi

# cleanup
rm -rf $TMP_DIR

### TODO more tests here
