======
ubuntu
======

Use Ubuntu cloud images as the baseline for built disk images.

Overrides:

 * To use a non-default URL for downloading base Ubuntu cloud images,
   use the environment variable ``DIB_CLOUD_IMAGES``
 * To download a non-default release of Ubuntu cloud images, use the
   environment variable ``DIB_RELEASE``. This element will export the
   ``DIB_RELEASE`` variable.

.. element_deps::
