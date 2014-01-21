Use Fedora cloud images as the baseline for built disk images.

Overrides:

 * To use a non-default URL for downloading base Fedora cloud images,
   use the environment variable DIB\_CLOUD\_IMAGES
 * To download a non-default release of Fedora cloud images, use the
   environment variable DIB\_RELEASE
 * Alternatively, set DIB\_LOCAL\_IMAGE to the local path of a qcow2 cloud
   image. This is useful in that you can use a customized or previously built
   cloud image from diskimage-builder as input. The cloud image does not have
   to have been build by diskimage-builder. It should be a full disk image,
   not just a filesystem image.
