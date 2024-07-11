========
Gentoo
========
Use a Gentoo cloud image as the baseline for built disk images. The images are
located in profile specific sub directories:

    http://distfiles.gentoo.org/releases/amd64/autobuilds/

As of this writing, only amd64 and arm64 images are available.

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

* The default profile is ``default/linux/amd64/23.0``.

* Any ``amd64`` or ``arm64`` profile with a stage tarball published by gentoo
  in the ``autobuilds`` directory for that arch are supported. Warning:
  the GENTOO_PROFILE environment variable will take precedence over the ARCH
  environment variable. 

* You can set the `GENTOO_PORTAGE_CLEANUP` environment variable to False to
  disable the clean up of portage repositories (including overlays).  This
  will make the image bigger if caching is also disabled.

* In many cases, the resulting image will not have a valid profile set. If
  you need to interactively use portage in a machine created with DIB, you
  will need to run `eselect profile set some/valid/profile` before interacting
  with portage.

* Gentoo supports many different versions of python, in order to select one
  you may use the `GENTOO_PYTHON_TARGETS` environment variable to select
  the versions of python you want on your image.  The format of this variable
  is a string as follows `"python3_10 python3_11"`. This variable only impacts
  the python versions used for distribution-installed python packages; see
  https://wiki.gentoo.org/wiki/Project:Python/PYTHON_TARGETS for more
  information.

* You can enable overlays using the `GENTOO_OVERLAYS` variable.  In it you
  should put a space separated list of overlays.  The overlays must be in the
  official overlay list and must be git based.

* `GENTOO_EMERGE_ENV` is a bash array containing default environment
  variables for package install, you can override it with another bash array.

* `GENTOO_EMERGE_DEFAULT_OPTS` can be set to control the default options
  passed to emerge for all package actions, this includes operations like
  depclean and preserved-rebuild.
