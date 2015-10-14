=====
rhel7
=====
Use RHEL 7 cloud images as the baseline for built disk images.

Because RHEL 7 base images are not publicly available, it is necessary to first
download the RHEL 7 cloud image from the Red Hat Customer Portal and pass the
path to the resulting file to disk-image-create as the ``DIB_LOCAL_IMAGE``
environment variable.

The cloud image can be found at (login required):
https://access.redhat.com/downloads/content/69/ver=/rhel---7/7.1/x86_64/product-downloads

Then before running the image build, define DIB_LOCAL_IMAGE (replace the file
name with the one downloaded, if it differs from the example)::
  export DIB_LOCAL_IMAGE=rhel-guest-image-7.1-20150224.0.x86_64.qcow2

The downloaded file will then be used as the basis for any subsequent image
builds.

For further details about building RHEL 7 images, see the rhel-common and
redhat-common element README files.

Environment Variables
---------------------

DIB_LOCAL_IMAGE
  :Required: Yes
  :Default: None
  :Description: The RHEL 7 base image you have downloaded. See the element
                description above for more details.
  :Example: ``DIB_LOCAL_IMAGE=/tmp/rhel7-cloud.qcow2``
