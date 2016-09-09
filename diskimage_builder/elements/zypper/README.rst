======
zypper
======
This element provides some customizations for zypper based distributions like
SLES and openSUSE. It works in a very similar way as the yum element does for
yum based distributions.

Zypper is reconfigured so that it keeps downloaded packages cached outside of
the build chroot so that they can be reused by subsequent image builds. The
cache increases image building speed when building multiple images, especially
on slow connections.  This is more effective than using an HTTP proxy for
caching packages since the download servers will often redirect clients to
different mirrors.
