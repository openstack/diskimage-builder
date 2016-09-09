===========
apt-sources
===========

Specify an apt sources.list file which is used during image building and then
remains on the image when it is run.

Environment Variables
---------------------

DIB_APT_SOURCES
  :Required: No
  :Default: None (Does not replace sources.list file)
  :Description: Path to a file on the build host which is used in place of
    ``/etc/apt/sources.list``
  :Example: ``DIB_APT_SOURCES=/etc/apt/sources.list`` will use the same
    sources.list as the build host.
