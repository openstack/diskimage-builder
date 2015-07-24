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

* The filename of the base image in the above repository is currently not
  stable (e.g. it includes a build number and image version). A fix for that
  will be rolled out to the repositories soon. A tempoary workaround to figure
  out the correct filename has been added to root.d/10-opensuse-cloud-image.
* Building with DIB\_EXTLINUX=1 doesn't work.  It fails with:
  /tmp/in\_target.d/finalise.d/51-bootloader: line 14: 16286 Segmentation fault
  extlinux --install /boot/syslinux
  (https://bugzilla.novell.com/show_bug.cgi?id=852856)
