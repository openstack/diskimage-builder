========
opensuse
========
Use an openSUSE cloud image as the baseline for built disk images. The images are
located in distribution specific sub directories under

    http://download.opensuse.org/repositories/Cloud:/Images:/

For example, the images of openSUSE 13.2 can be found here:

    http://download.opensuse.org/repositories/Cloud:/Images:/openSUSE_13.2/images/

These images should be considered experimental. There are curently only x86_64
images.

Notes:

* There are very frequently new automated builds that include changes that
  happen during the product maintenance. The download directories contain an
  unversioned name and a versioned name. The unversioned name will always
  point to the latest image, but will frequently change its content. The versioned
  one will never change content, but will frequently be deleted and replaced
  by a newer build with a higher version-release number.

* Building with DIB\_EXTLINUX=1 doesn't work.  It fails with:
  /tmp/in\_target.d/finalise.d/51-bootloader: line 14: 16286 Segmentation fault
  extlinux --install /boot/syslinux
  (https://bugzilla.novell.com/show_bug.cgi?id=852856)
