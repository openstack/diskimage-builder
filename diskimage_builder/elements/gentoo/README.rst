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

    default/linux/amd64/17.0
    default/linux/amd64/17.0/no-multilib
    default/linux/amd64/17.0/hardened
    default/linux/amd64/17.0/no-multilib/hardened

* You can set the GENTOO_PORTAGE_CLEANUP environment variable to true (or
  anything other than False) to clean up portage from the system and get the
  image size smaller.

* Gentoo supports many diferent versions of python, in order to select one
  you may use the `GENTOO_PYTHON_TARGETS` environment variable to select
  the versions of python you want on your image.  The format of this variable
  is a string as follows `"python2_7 python3_5"`.

* In addition you can select the primary python version you wish to use (that
  which will be called by running the `python` command.  The
  `GENTOO_PYTHON_ACTIVE_VERSION` is used to set that mapping.  The variable
  contents can be something like `python3.5`.

* You can enable overlays using the `GENTOO_OVERLAYS` variable.  In it you
  should put a space separated list of overlays.  The overlays must be in the
  official overlay list and must be git based.
