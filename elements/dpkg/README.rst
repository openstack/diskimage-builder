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

* DIB\_ADD\_APT\_KEYS: If an extra or updated apt key is needed then define
  DIB\_ADD\_APT\_KEYS with the path to a folder. Any key files inside will be
  added to the key ring before any apt-get commands take place.
* DIB\_APT\_LOCAL\_CACHE: You can use this variable to disable the internal cache
  of the /var/cache/apt/archives directory by setting it to 0. The default is to bind
  mount the $DIB_IMAGE_CACHE/apt/$DISTRO_NAME directory in
  /var/cache/apt/archives, this to cache the .deb files downloaded during the image
  creation.
* At the end of a dib run we clean the apt cache to keep the image size as
  small as possible. You can set DIB\_DISABLE\_APT\_CLEANUP=1 if you would
  like to prevent this.
