==============
fedora-minimal
==============

*Note* as at February 2022, this element is no longer tested or used
by OpenDev.  Changes to the RPM format used by recent Fedora releases
have meant that this element can not build on Ubuntu hosts, which lack
a packaged RPM sufficient to extract the base chroot environment.  The
``fedora-containerfile`` element can be used instead of this element.

Create a minimal image based on Fedora.

Use of this element will require 'yum' and 'yum-utils' to be installed on
Ubuntu and Debian. Nothing additional is needed on Fedora or CentOS. The
element will need `python-lzma` everywhere.

Due to a bug in the released version of urlgrabber, on many systems an
installation of urlgrabber from git is required. The git repository
can be found here: http://yum.baseurl.org/gitweb?p=urlgrabber.git;a=summary

This element sets the ``DISTRO_NAME`` var to 'fedora'. The release of
fedora to be installed can be controlled through the ``DIB_RELEASE``
variable, which defaults the latest supported release.
