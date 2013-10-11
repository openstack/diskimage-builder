Use an openSUSE cloud image as the baseline for built disk images. The base
image is located here:

    http://download.opensuse.org/repositories/Cloud:/Images/images/

This image should currently be considered experimental. Right now, we've only
got a 64 bit image, and no 32 bit image. But it's a start.

Notes:

* The filename of the base image in the above repository is currently not
  stable (e.g. it includes a build number and image version). A fix for that
  will be rolled out to the repositories soon. A tempoary workaround to figure
  out the correct filename has been added to root.d/10-opensuse-cloud-image.
* Building with DIB\_EXTLINUX=1 doesn't work.  It fails with:
  /tmp/in\_target.d/finalise.d/51-bootloader: line 14: 16286 Segmentation fault
  extlinux --install /boot/syslinux
  (https://bugzilla.novell.com/show_bug.cgi?id=852856)
* This element doesn't need half of the rpm-distro element's pre-install
  hooks.  The exceptions are 01-install-bin, which has been copied to
  this element, and 01-override-zypp-arch (which is something that
  could probably be jammed into the base image...).
* We might want to use the local-config element (after updating that element to
  inject http\_proxy properly for openSUSE, of course).
  (https://bugs.launchpad.net/diskimage-builder/+bug/1256982)

