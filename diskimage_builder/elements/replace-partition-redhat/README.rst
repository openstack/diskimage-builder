========================
replace-partition-redhat
========================

A redhat family specific version of the ``replace-partition`` element.

A standalone element which consumes a base image which was created with
``diskimage-builder`` and rebuilds it without making any packaging changes.

Example
=======

The following will use ``./my-dib-image.qcow2`` as the base image and create a
new image ``my-dib-image-custom.qcow2`` with the partition layout defined in
``./block-device-custom.yaml``:

.. code-block:: bash

    export DISTRO_NAME=rhel
    export DIB_BLOCK_DEVICE_CONFIG=file://./block-device-custom.yaml
    export DIB_LOCAL_IMAGE=./my-dib-image.qcow2
    disk-image-create -x -a x86_64 -o my-dib-image-custom.qcow2 --image-size 6GiB replace-partition-redhat
