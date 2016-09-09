===========
ubuntu-core
===========
Use Ubuntu Core cloud images as the baseline for built disk images.

Overrides:

 * To use a non-default URL for downloading base Ubuntu cloud images,
   use the environment variable DIB\_CLOUD\_IMAGES
 * To download a non-default release of Ubuntu cloud images, use the
   environment variable DIB\_RELEASE
 * To use different mirrors rather than the default of archive.ubuntu.com and
   security.ubuntu.com, use the environment variable DIB\_DISTRIBUTION\_MIRROR
