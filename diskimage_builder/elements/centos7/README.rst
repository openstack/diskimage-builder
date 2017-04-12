=======
centos7
=======
Use Centos 7 cloud images as the baseline for built disk images.

For further details see the redhat-common README.

DIB_DISTRIBUTION_MIRROR:
   :Required: No
   :Default: None
   :Description: To use a CentOS Yum mirror, set this variable to the mirror URL
                 before running bin/disk-image-create. This URL should point to
                 the directory containing the ``5/6/7`` directories.
   :Example: ``DIB_DISTRIBUTION_MIRROR=http://amirror.com/centos``

DIB_CLOUD_IMAGES
  :Required: No
  :Description: Set the desired URL to fetch the images from.  ppc64le:
                Currently the CentOS community is working on providing the
                ppc64le images until then you'll need to set this to a local
                image file.
