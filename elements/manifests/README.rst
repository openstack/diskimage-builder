=========
manifests
=========

An framework for saving manifest information generated during the
build for later inspection.  Manifests are kept in the final image and
also copied to the build area post-image creation.

Elements that wish to save any form of manifest should depend on this
element and can save their data to into the ``DIB_MANIFEST_IMAGE_DIR`` (
which defaults to ``/etc/dib-manifests``).  Note this is created in
``extra-data.d`` rather than ``pre-install.d`` to allow the
``source-repositories`` element to make use of it

The manifests are copied to ``DIB_MANIFEST_SAVE_DIR``, which defaults
to ``${IMAGE_NAME}.d/``, resulting in the manifests being available as
``${IMAGE_NAME}.d/dib-manifests`` by default after the build.

Extra status
------------

This element will also add the files ``dib_environment`` and
``dib_arguments`` to the manifest recording the ``diskimage-builder``
specific environment (``DIB_*`` variables) and command-line arguments
respectively.
