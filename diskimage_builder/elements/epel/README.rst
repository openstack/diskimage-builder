====
epel
====
This element installs the Extra Packages for Enterprise Linux (EPEL)
repository GPG key as well as configuration for yum.

DIB_EPEL_MIRROR:
   :Required: No
   :Default: None
   :Description: To use a EPEL Yum mirror, set this variable to the mirror URL
                 before running bin/disk-image-create. This URL should point to
                 the directory containing the ``5/6/7`` directories.
   :Example: ``DIB\_EPEL\_MIRROR=http://dl.fedoraproject.org/pub/epel``
