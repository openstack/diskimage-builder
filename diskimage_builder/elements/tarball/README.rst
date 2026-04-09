=======
tarball
=======

Base element for creating images from a pre-built OS root filesystem tarball.

This element is intended for use in unprivileged container environments where
device mapper (required by ``qcow2``-based elements) and FUSE (required by
``containerfile``-based elements) are not available. The OS root filesystem
is sourced from a tarball on the host, moving the task of obtaining the OS
content entirely outside the disk image build process.

The tarball should contain the root filesystem of the target OS (i.e. the
contents that will be extracted directly into ``$TARGET_ROOT``).

Environment Variables
---------------------

``DIB_TARBALL_PATH``
    *Required.* Absolute path to the tarball on the host filesystem. The
    tarball must contain a complete OS root filesystem. Supported formats
    are any archive format accepted by GNU tar (e.g. ``.tar``, ``.tar.gz``,
    ``.tar.bz2``, ``.tar.xz``, ``.tar.zst``).

``DISTRO_NAME``
    *Optional.* The name of the OS distribution contained in the tarball
    (e.g. ``ubuntu``, ``centos``). Defaults to ``tarball``. Setting this
    correctly allows other elements that condition on ``DISTRO_NAME`` to
    behave as expected.

``DIB_RELEASE``
    *Optional.* The release identifier of the OS distribution (e.g.
    ``noble``, ``9-stream``). Defaults to ``unknown``.

Example
-------

.. code-block:: shell

    export DIB_TARBALL_PATH=/path/to/ubuntu-noble-rootfs.tar.gz
    export DISTRO_NAME=ubuntu
    export DIB_RELEASE=noble
    disk-image-create -o my-image tarball my-other-element
