Create an image based on Debian. We default to unstable but DIB_RELEASE
is mapped to any series of Debian.

Note that the default Debian series is `unstable`, and the default
mirrors for Debian can be problematic for `unstable`. Because apt does
not handle changing Packages files well across multiple out of sync
mirrors, it is recommended that you choose a single mirror of debian,
and pass it in via `DIB_DISTRIBUTION_MIRROR`.

Use of this element will also require the tool 'debootstrap' to be
available on your system. It should be available on Ubuntu, Debian,
and Fedora.
