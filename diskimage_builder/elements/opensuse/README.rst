========
opensuse
========
Use an openSUSE cloud image as the baseline for built disk images. The images are
located in distribution specific sub directories under

    http://download.opensuse.org/repositories/Cloud:/Images:/

These images should be considered experimental. There are currently only x86_64
images.

Environment Variables
---------------------

DIB_RELEASE
  :Required: No
  :Default: 42.3
  :Description: Set the desired openSUSE release.

DIB_CLOUD_IMAGES
  :Required: No
  :Default: http://download.opensuse.org/repositories/Cloud:/Images:/(openSUSE|Leap)_${DIB_RELEASE}
  :Description: Set the desired URL to fetch the images from.

Notes:

* There are very frequently new automated builds that include changes that
  happen during the product maintenance. The download directories contain an
  unversioned name and a versioned name. The unversioned name will always
  point to the latest image, but will frequently change its content. The versioned
  one will never change content, but will frequently be deleted and replaced
  by a newer build with a higher version-release number.
