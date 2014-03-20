Image installation steps common to RHEL and Fedora.

Overrides:

 * To use a non-default URL for downloading base cloud images,
   use the environment variable DIB_CLOUD_IMAGES
 * To download a non-default release of cloud images, use the
   environment variable DIB_RELEASE
 * Alternatively, set DIB_LOCAL_IMAGE to the local path of a qcow2 cloud
   image. This is useful in that you can use a customized or previously built
   cloud image from diskimage-builder as input. The cloud image does not have
   to have been built by diskimage-builder. It should be a full disk image,
   not just a filesystem image.