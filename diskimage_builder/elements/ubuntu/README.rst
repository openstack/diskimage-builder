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
 * Use ``DIB_DISTRIBUTION_MIRROR`` to override the ``sources.list``
   with an alternative mirror
 * Setting ``DIB_DISTRIBUTION_MIRROR_UBUNTU_IGNORE`` to an
   extended-regexp (i.e. the argument to the ``=~`` bash comparitor)
   which, when matched, will *not* set that line to the
   ``DIB_DISTRIBUTION_MIRROR``.  For example, if your local mirror
   does not mirror the universe and multiverse components, set this to
   ``(universe|multiverse)``
 * Setting ``DIB_DISTRIBUTION_MIRROR_UBUNTU_INSECURE`` updates apt
   settings to allow insecure/unuthenticated repositories.
 * Setting ``DIB_OFFLINE`` will prevent to download again the source image
   if is already present in to $DIB_IMAGE_CACHE path.
 * Setting ``DIB_LOCAL_IMAGE`` to use a image from a local source (full path and file name)
   and not download image from internet. Local source for release Trusty
   have to be tar.gz format. For other more recent release get the squashfs image.

.. element_deps::
