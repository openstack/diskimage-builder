================
opensuse-minimal
================

This element will build a minimal openSUSE image. It requires 'zypper' to be
installed on the host.

These images should be considered experimental. There are curently only x86_64
images.

Environment Variables
---------------------

DIB_RELEASE
  :Required: No
  :Default: 42.2
  :Description: Set the desired openSUSE release.

DIB_OPENSUSE_MIRROR:
   :Required: No
   :Default: http://download.opensuse.org
   :Description: To use a specific openSUSE mirror, set this variable to the
                 mirror URL before running bin/disk-image-create. This URL
                 should point to the root directory as indicated in the
                 http://mirrors.opensuse.org/ webpage. You normally
                 don't want to change that since the default setting will
                 pick the mirror closest to you.
   :Example: ``DIB_OPENSUSE_MIRROR=http://ftp.cc.uoc.gr/mirrors/linux/opensuse/opensuse/``
