Create an image based on Debian. We default to unstable but DIB_RELEASE
is mapped to any series of Debian.

Note that the default Debian series is `unstable`, and the default
mirrors for Debian can be problematic for `unstable`. Because apt does
not handle changing Packages files well across multiple out of sync
mirrors, it is recommended that you choose a single mirror of debian,
and pass it in via `DIB_DISTRIBUTION_MIRROR`.

If necessary, a custom apt keyring and debootstrap script can be
supplied to the `debootstrap` command via `DIB_DEBIAN_KEYRING` and
`DIB_DEBIAN_DEBOOTSTRAP_SCRIPT` respectively. Both options require the
use of absolute rather than relative paths.

Use of this element will also require the tool 'debootstrap' to be
available on your system. It should be available on Ubuntu, Debian,
and Fedora.

The `DIB_OFFLINE` or more specific `DIB_DEBIAN_USE_DEBOOTSTRAP_CACHE`
variables can be set to prefer the use of a pre-cached root filesystem
tarball.
