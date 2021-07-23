======
rocky
======

Use RockyLinux cloud images as the baseline for built disk images.

For further details see the redhat-common README.

Environment Variables
---------------------

DIB_DISTRIBUTION_MIRROR:
   :Required: No
   :Default: None
   :Description: To use a Rocky Yum mirror, set this variable to the mirror URL
                 before running bin/disk-image-create. This URL should point to
                 the directory containing the `8` directories.
   :Example: ``DIB_DISTRIBUTION_MIRROR=http://amirror.com/rocky``
   