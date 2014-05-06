# Create package pins for apt systems if packages need to be held back

For APT based systems, you specify package priorities in the apt preferences file.
This element reads the given manifest file, specified in `DIB_DPKG_MANIFEST`, to
set pins to enable pinning of older versions for the given packages.

