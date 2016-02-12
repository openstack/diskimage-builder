==============
debian-minimal
==============

Create a minimal image based on Debian. We default to unstable but DIB_RELEASE
is mapped to any series of Debian.

Note that the default Debian series is `unstable`, and the default
mirrors for Debian can be problematic for `unstable`. Because apt does
not handle changing Packages files well across multiple out of sync
mirrors, it is recommended that you choose a single mirror of debian,
and pass it in via `DIB_DISTRIBUTION_MIRROR`.

By default only `main` component is used. If `DIB_DEBIAN_COMPONENTS` (comma
separated) from the `debootstrap` element has been set, that list of
components will be used instead.

Backports are included unless `DIB_RELEASE` is `unstable`.

If necessary, a custom apt keyring and debootstrap script can be
supplied to the `debootstrap` command via `DIB_APT_KEYRING` and
`DIB_DEBIAN_DEBOOTSTRAP_SCRIPT` respectively. Both options require the
use of absolute rather than relative paths.

Use of this element will also require the tool 'debootstrap' to be
available on your system. It should be available on Ubuntu, Debian,
and Fedora. It is also recommended that the 'debian-keyring' package
be installed.

The `DIB_OFFLINE` or more specific `DIB_DEBIAN_USE_DEBOOTSTRAP_CACHE`
variables can be set to prefer the use of a pre-cached root filesystem
tarball.

The `DIB_DEBOOTSTRAP_EXTRA_ARGS` environment variable may be used to
pass extra arguments to the debootstrap command used to create the
base filesystem image. If --keyring is is used in `DIB_DEBOOTSTRAP_EXTRA_ARGS`,
it will override `DIB_APT_KEYRING` if that is used as well.

-------------------
Note on ARM systems
-------------------

Because there is not a one-to-one mapping of `ARCH` to a kernel package, if
you are building an image for ARM on debian, you need to specify which kernel
you want in the environment variable `DIB_ARM_KERNEL`. For instance, if you want
the `linux-image-mx5` package installed, set `DIB_ARM_KERNEL` to `mx5`.
