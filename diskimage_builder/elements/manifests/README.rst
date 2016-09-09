=========
manifests
=========
Copy any manifests generated into the build area post-image creation

This element should be a dependency of any element that writes a manifest
into the `DIB_MANIFEST_IMAGE_DIR`, which defaults to `/etc/dib-manifests`.
This is created in extra-data.d rather than pre-install.d to allow the
source-repositories element to make use of it

The manifests are copied to `DIB_MANIFEST_SAVE_DIR`, which defaults to
`${IMAGE_NAME}.d/`, resulting in the manifests being available as
`${IMAGE_NAME}.d/dib-manifests` by default
