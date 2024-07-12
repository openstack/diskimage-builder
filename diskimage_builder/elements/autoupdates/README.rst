===========
autoupdates
===========

This element will configure both debian family and redhat family images to have an automatic updates mechanism built into the image, for example to update automatically from the security repos.
For Debian based images it is based on unuattended-upgrades and for Redhat on dnf-automatic.

Environment Variables
---------------------

DIB_DEB_UPDATES_CONF
   :Required: Yes for the Debian Family
   :Default: None
   :Description: The location of a custom 50unattended-upgrades file on the builder which will be injected into the image.
   :Example: ``DIB_DEB_UPDATES_CONF=/home/50unattended-upgrades``

DIB_YUM_UPDATES_CONF
   :Required: Yes for the Redhat Family
   :Default: None
   :Description: The location of a custom automatic.conf file on the builder which will be injected into the image.
   :Example: ``DIB_YUM_UPDATES_CONF=/home/automatic.conf``

.. element_deps::
