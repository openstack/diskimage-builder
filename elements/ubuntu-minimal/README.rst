==============
ubuntu-minimal
==============

Note: The ubuntu element is likely what you want unless you really know
you want this one for some reason. The ubuntu element gets a lot more testing
coverage and use.

Create a minimal image based on Ubuntu. We default to trusty but DIB_RELEASE
is mapped to any series of Ubuntu.

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
