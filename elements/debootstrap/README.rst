===========
debootstrap
===========

Base element for creating minimal debian-based images.

This element is incomplete by itself, you'll want to use the debian-minimal
or ubuntu-minimal elements to get an actual base image.

If necessary, a custom apt keyring and debootstrap script can be
supplied to the `debootstrap` command via `DIB_APT_KEYRING` and
`DIB_DEBIAN_DEBOOTSTRAP_SCRIPT` respectively. Both options require the
use of absolute rather than relative paths.

Use of this element will also require the tool 'debootstrap' to be
available on your system. It should be available on Ubuntu, Debian,
and Fedora.

The `DIB_OFFLINE` or more specific `DIB_DEBIAN_USE_DEBOOTSTRAP_CACHE`
variables can be set to prefer the use of a pre-cached root filesystem
tarball.

The `DIB_DEBOOTSTRAP_EXTRA_ARGS` environment variable may be used to
pass extra arguments to the debootstrap command used to create the
base filesystem image. If --keyring is is used in `DIB_DEBOOTSTRAP_EXTRA_ARGS`,
it will override `DIB_APT_KEYRING` if that is used as well.

The `DIB_DEBOOTSTRAP_CACHE` variable can be used to cache the created root
filesystem. By default this is 0 (disabled) and any other value enables this.
If run in offline mode then the most recently cached rootfs is used instead of
being built.

The `DIB_DEBOOTSTRAP_DEFAULT_LOCALE` environment variable may be used
to configure the default locale of the base image. It defaults to
C.UTF-8.

-------------------
Note on ARM systems
-------------------

Because there is not a one-to-one mapping of `ARCH` to a kernel package, if
you are building an image for ARM on debian, you need to specify which kernel
you want in the environment variable `DIB_ARM_KERNEL`. For instance, if you want
the `linux-image-mx5` package installed, set `DIB_ARM_KERNEL` to `mx5`.
