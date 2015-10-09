=============
redhat-common
=============
Image installation steps common to RHEL, CentOS, and Fedora.

Requirements:

If used to build an image form a cloud image compress with xz
(the default in centos), this element uses "unxz" to decompress
the image. Depending on your distro you may need to install either
the xz or xz-utils package.

Environment Variables
---------------------

DIB_LOCAL_IMAGE
  :Required: No
  :Default: None
  :Description: Use the local path of a qcow2 cloud image. This is useful in
   that you can use a customized or previously built cloud image from
   diskimage-builder as input. The cloud image does not have to have been built
   by diskimage-builder. It should be a full disk image, not just a filesystem
   image.
  :Example: ``DIB_LOCAL_IMAGE=rhel-guest-image-7.1-20150224.0.x86_64.qcow2``
