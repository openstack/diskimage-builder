======
fedora
======

Use Fedora cloud images as the baseline for built disk images. For further
details see the redhat-common README.

Releases
--------

This element targets the current and previous version of Fedora; these
values clearly changes over time.  To fix the version set the
`DIB_RELEASE` variable to the Fedora version (e.g. ``36``).  The
default value is the current best supported version (i.e. it may
change upward at any given release to support the next Fedora).


Environment Variables
---------------------

DIB_DISTRIBUTION_MIRROR:
   :Required: No
   :Default: None
   :Description: To use a Fedora Yum mirror, set this variable to the mirror URL
                 before running bin/disk-image-create. This URL should point to
                 the directory containing the ``releases/updates/development``
                 and ``extras`` directories.
   :Example: ``DIB\_DISTRIBUTION\_MIRROR=http://download.fedoraproject.org/pub/fedora/linux``


