======
fedora
======

Use Fedora cloud images as the baseline for built disk images. For further
details see the redhat-common README.

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


