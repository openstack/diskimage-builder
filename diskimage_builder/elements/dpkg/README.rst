====
dpkg
====
Provide dpkg specific image building glue.

The ubuntu element needs customisations at the start and end of the image build
process that do not apply to RPM distributions, such as using the host machine
HTTP proxy when installing packages. These customisations live here, where they
can be used by any dpkg based element.

The dpkg specific version of install-packages is also kept here.

Environment Variables
---------------------

DIB_APT_KEYS
  :Required: No
  :Default: None
  :Description: If an extra or updated apt key is needed then define
    ``DIB_ADD_APT_KEYS`` with the path to a folder. Any key files inside will be
    added to the key ring before any apt-get commands take place.
  :Example: ``DIB_APT_KEYS=/etc/apt/trusted.gpg.d``

DIB_APT_LOCAL_CACHE
  :Required: No
  :Default: 1
  :Description: By default the ``$DIB_IMAGE_CACHE/apt/$DISTRO_NAME`` directory is
    mounted in ``/var/cache/apt/archives`` to cache the .deb files downloaded
    during the image creation. Use this variable if you wish to disable the
    internal cache of the ``/var/cache/apt/archives`` directory
  :Example: ``DIB_APT_LOCAL_CACHE=0`` will disable internal caching.

DIB_DISABLE_APT_CLEANUP
  :Required: No
  :Default: 0
  :Description: At the end of a dib run we clean the apt cache to keep the image
    size as small as possible. Use this variable to prevent cleaning the apt cache
    at the end of a dib run.
  :Example: ``DIB_DISABLE_APT_CLEANUP=1`` will disable cleanup.

