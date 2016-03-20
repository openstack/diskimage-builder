========
Gentoo
========
Use a Gentoo cloud image as the baseline for built disk images. The images are
located in profile specific sub directories:

    http://distfiles.gentoo.org/releases/amd64/autobuilds/

As of this writing, only x86_64 images are available.

Notes:

* There are very frequently new automated builds that include changes that
  happen during the product maintenance. The download directories contain an
  unversioned name and a versioned name. The unversioned name will always
  point to the latest image, but will frequently change its content. The
  versioned one will never change content, but will frequently be deleted and
  replaced by a newer build with a higher version-release number.

* In order to run the package-installs element you will need to make sure
  `dev-python/pyyaml` is installed on the host.

* In order to run the vm element you will need to make sure `sys-block/parted`
  is installed on the host.

* Other profiles can be used by exporting GENTOO_PROFILE with a valid profile.
  A list of valid profiles follows:

    default/linux/amd64/13.0
    default/linux/amd64/13.0/no-multilib
    hardened/linux/amd64
    hardened/linux/amd64/no-multilib
