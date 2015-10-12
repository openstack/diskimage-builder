===============
apt-preferences
===============

This element generates the APT preferences file based on the provided manifest
provided by the :doc:`../manifests/README` element.

The APT preferences file can be used to control which versions of packages will
be selected for installation. APT uses a priority system to make this
determination. For more information about APT preferences, see the apt_preferences(5)
man page.

Environment Variables
---------------------

DIB_DPKG_MANIFEST:
   :Required: No
   :Default: None
   :Description: The manifest file to generate the APT preferences file from.
   :Example: ``DIB\_DPKG\_MANIFEST=~/image.d/dib-manifests/dib-manifest-dpkg-image``

