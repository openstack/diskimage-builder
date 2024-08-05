======
centos
======

Use CentOS cloud images as the baseline for built disk images.

For further details see the redhat-common README.

Environment Variables
---------------------

DIB_DISTRIBUTION_MIRROR:
   :Required: No
   :Default: None
   :Description: To use a CentOS Yum mirror, set this variable to the mirror URL
                 before running bin/disk-image-create. This URL should point to
                 the directory containing the ``7/8-stream/9-stream`` directories.
   :Example: ``DIB_DISTRIBUTION_MIRROR=http://amirror.com/centos``

DIB_CLOUD_IMAGES:
  :Required: No
  :Description: Set the desired URL to fetch the images from.  ppc64le:
                Currently the CentOS community is working on providing the
                ppc64le images. Until then you'll need to set this to a local
                image file.
  :Example: ``DIB_CLOUD_IMAGES=/path/to/my/centos/8/CentOS-8-GenericCloud-x86_64.qcow2``

DIB_RELEASE:
  :Required: No
  :Description: To override the release to build, utilize this paraemter.
                Presently defaults to ``9-stream``, however may be changed by
                diskimage-builder to newer versions *as* the distribution
                versions move through their lifecycle.
