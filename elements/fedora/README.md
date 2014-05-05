Use Fedora cloud images as the baseline for built disk images.

If you wish to use a Fedora Yum mirror you can set DIB\_DISTRIBUTION\_MIRROR
before running bin/disk-image-create. Example:

  DIB\_DISTRIBUTION\_MIRROR=http://download.fedoraproject.org/pub/fedora/linux

This URL should point to the directory containing the releases/updates/
development/and extras directories.

For further details see the redhat-common README.
