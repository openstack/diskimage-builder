==========
enable-services
==========

Enables services inside the generated cloud image.
Currently only supports Gentoo, and only OpenRC's default runlevel, as well as only systemd service units.

Environment Variables
---------------------

DIB_ENABLE_SERVICES:
  :Required: No
  :Default: Empty
  :Description: Enables services post-install for the generated cloud image.
  :Example: DIB_ENABLE_SERVICES="systemd-networkd systemd-resolved"
