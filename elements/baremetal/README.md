This is the baremetal (IE: real hardware) element.

Does the following:

 * Enables stable network interface naming (em1, em2, etc) by
   installing the biosdevname and removes any symlinks which may
   disable udev rules, etc.

 * extracts the kernel and initial ramdisk of the built image.
