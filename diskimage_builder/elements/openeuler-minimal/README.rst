=================
openeuler-minimal
=================
Create a minimal image from scratch.

Use of this element will require 'yum' and 'yum-utils' to be installed on
Ubuntu and Debian. Nothing additional is needed on Fedora, CentOS or
openEuler.

Set ``DIB_RELEASE`` to ``22.03-LTS`` other release number to explicitly select
the release. ``DIB_RELEASE`` defaults the latest LTS release.

Set ``DIB_DISTRIBUTION_MIRROR`` to the mirror URL use a openEuler Yum mirror.
This URL should point to the directory containing the ``DIB_RELEASE``
directories.
