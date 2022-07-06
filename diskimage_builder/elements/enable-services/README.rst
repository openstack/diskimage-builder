==========
enable-services
==========

Enables services (like networking) for the generated cloud image.
Currently only supports Gentoo, and only OpenRC's default runlevel, as well as only systemd Service units.  More may come later.
If you enable this element, and do not specify DIB_ENABLE_SERVICES, it does nothing.
If you enable this element on any distro that is not Gentoo, it also does nothing.

Environment Variables
---------------------

DIB_ENABLE_SERVICES:
  :Required: No
  :Default: Empty
  :Description: Enables services post-install for the generated cloud image.
