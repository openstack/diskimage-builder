====
rhel
====

Use RHEL cloud images as the baseline for built disk images.

Because RHEL base images are not publicly available, it is necessary to first
download the RHEL cloud image from the Red Hat Customer Portal and pass the
path to the resulting file to disk-image-create as the ``DIB_LOCAL_IMAGE``
environment variable.

The cloud image can be found at (login required):
RHEL8: https://access.redhat.com/downloads/content/479/ver=/rhel---8/8.0/x86_64/product-software
RHEL7: https://access.redhat.com/downloads/content/69/ver=/rhel---7/7.1/x86_64/product-downloads


Then before running the image build, define DIB_LOCAL_IMAGE (replace the file
name with the one downloaded, if it differs from the example):

.. code-block:: bash

   export DIB_LOCAL_IMAGE=rhel-8.0-x86_64-kvm.qcow2

The downloaded file will then be used as the basis for any subsequent image
builds.

For further details about building RHEL images, see the rhel-common and
redhat-common element README files.

Environment Variables
---------------------

DIB_LOCAL_IMAGE
  :Required: Yes
  :Default: None
  :Description: The RHEL 8 base image you have downloaded. See the element
                description above for more details.
  :Example: ``DIB_LOCAL_IMAGE=/tmp/rhel8-cloud.qcow2``


