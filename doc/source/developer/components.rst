Components
==========

`disk-image-create [-a amd64|armhf|arm64] -o filename {element} [{element} ...]`

    Create an image of element {element}, optionally mixing in other elements.
    Element dependencies are automatically included. Support for other
    architectures depends on your environment being able to run binaries of
    that platform and/or packages being available for the architecture. For
    instance, to enable armhf on Ubuntu install the qemu-user-static package,
    or to enable arm64 on CentOS setup the RDO aarch64 package repositories.
    The default output format from disk-image-create is qcow2. To instead
    output a tarball pass in "-t tar". This tarball could then be used as an
    image for a linux container(see docs/docker.md).

`ramdisk-image-create -o filename {element} [{element} ...]`

    Create a kernel+ ramdisk pair for running maintenance on bare metal
    machines (deployment, inventory, burnin etc).

    To generate kernel+ramdisk pair for use with nova-baremetal, use::

        ramdisk-image-create -o deploy.ramdisk deploy-baremetal

    Ironic no longer supports images created like this.

`diskimage-builder [--dry-run] [--stop-on-failure] [--help] filename.yaml [filename2.yaml...]`

    A YAML defined wrapper over `disk-image-create` and `ramdisk-image-create`.

    To generate kernel+ramdisk pair for use with nova-baremetal, specify the YAML:

    .. code-block:: yaml

        - imagename: deploy.ramdisk
          ramdisk: true
          elements:
          - deploy-baremetal

    Duplicate `imagename` entries are merged into a single entry, allowing customizations over
    a base image definition. If an `imagename` is missing, the `imagename` from the previous
    entry is implied:

    .. code-block:: yaml

        # base image definition
        - imagename: output.qcow
          elements:
          - vm
          - block-device-gpt
          - ubuntu-minimal
          debug-trace: 1
          environment:
            DIB_IMAGE_SIZE: '10'

        # debug logging customization
        - imagename: output.qcow
          debug-trace: 2

        # adding element customization
        - elements:
          - devuser
          environment:
            DIB_DEV_USER_USERNAME: 'myuser'
            DIB_DEV_USER_PWDLESS_SUDO: 'Yes'
            DIB_DEV_USER_AUTHORIZED_KEYS: '/home/myuser/.ssh/id_rsa.pub'

        # resulting image entry which will be built
        - imagename: output.qcow
          elements:
          - vm
          - block-device-gpt
          - ubuntu-minimal
          - devuser
          debug-trace: 2
          environment:
            DIB_DEV_USER_USERNAME: 'myuser'
            DIB_DEV_USER_PWDLESS_SUDO: 'Yes'
            DIB_DEV_USER_AUTHORIZED_KEYS: '/home/myuser/.ssh/id_rsa.pub'
            DIB_IMAGE_SIZE: '10'

`element-info`

    Extract information about elements.

`tests/run_functests.sh`

    This runs a set of functional tests for diskimage-builder.

elements can be found in the top level elements directory.
