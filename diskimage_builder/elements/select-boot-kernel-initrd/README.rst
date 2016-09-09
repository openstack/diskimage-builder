=========================
select-boot-kernel-initrd
=========================
A helper script to get the kernel and initrd image.

It uses the function select_boot_kernel_initrd from the library img-functions
to find the newest kernel and ramdisk in the image, and returns them as a
concatenated string separating the values with a colon (:).
