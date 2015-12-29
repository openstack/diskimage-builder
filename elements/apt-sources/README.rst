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

DIB_APT_SOURCES_INLINE
  :Required: No
  :Default: None (Does not replace sources.list file)
  :Description: Array of sources.list values to be used
  :Example: B_APT_SOURCES_INLINE=(
    "deb http://mirror.servers.com/debian/ jessie main contrib non-free"
    "deb-src http://mirror.servers.com/debian/ jessie main contrib non-free"
    )

Note: You should use or DIB_APT_SOURCES or DIB_APT_SOURCES_INLINE, but not 
the both same time.

