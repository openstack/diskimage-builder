Provide dpkg specific image building glue.

The ubuntu element needs customisations at the start and end of the image build
process that do not apply to RPM distributions, such as using the host machine
HTTP proxy when installing packages. These customisations live here, where they
can be used by any dpkg based element.

The dpkg specific version of install-packages is also kept here.

If an extra or updated apt key is needed then define DIB\_ADD\_APT\_KEYS with
the path to a folder. Any key files inside will be added to the key ring before
any apt-get commands take place.
