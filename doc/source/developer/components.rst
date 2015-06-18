Components
==========

`disk-image-create [-a i386|amd64|armhf] -o filename {element} [{element} ...]`

    Create an image of element {element}, optionally mixing in other elements.
    Element dependencies are automatically included. Support for other
    architectures depends on your environment being able to run binaries of
    that platform. For instance, to enable armhf on Ubuntu install the
    qemu-user-static package. The default output format from disk-image-create
    is qcow2. To instead output a tarball pass in "-t tar". This tarball could
    then be used as an image for a linux container(see docs/docker.md).

`ramdisk-image-create -o filename {element} [{element} ...]`

    Create a kernel+ ramdisk pair for running maintenance on bare metal
    machines (deployment, inventory, burnin etc).

    To generate kernel+ramdisk pair for use with nova-baremetal, use::

        ramdisk-image-create -o deploy.ramdisk deploy-baremetal

    To generate kernel+ramdisk pair for use with ironic, use::

        ramdisk-image-create -o deploy.ramdisk deploy-ironic


`element-info`

    Extract information about elements.

`tests/run_functests.sh`

    This runs a set of functional tests for diskimage-builder.

elements can be found in the top level elements directory.
