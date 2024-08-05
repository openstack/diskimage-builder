===
yum
===
Provide yum specific image building glue.

RHEL/Fedora/CentOS and other yum based distributions need specific yum
customizations.

Customizations include caching of downloaded yum packages outside of the build
chroot so that they can be reused by subsequent image builds.  The cache
increases image building speed when building multiple images, especially on
slow connections.  This is more effective than using an HTTP proxy as a yum
cache since the same rpm from different mirrors is often requested.

Custom yum repository configurations can also be applied by defining
`DIB_YUM_REPO_CONF` to a space separated list of repo configuration files. The
files will be copied to /etc/yum.repos.d/ during the image build, and then
removed at the end of the build. Each repo file should be named differently to
avoid a filename collision.

The yum repository can also be configured by defining `DIB_YUM_REPO_PACKAGE` as
a yum available package or a URL to an rpm file. This package can install repo
files with any associated keys and certificates.

Environment Variables
---------------------

DIB_DNF_MODULE_STREAMS
  :Required: No
  :Default: None
  :Description: The following environment variable is used to select module streams
                to be enabled during an image build on Yum/DNF based distributions.Any existing
                stream for the given module is first disabled prior to enabling the specified
                stream.
  :Example: ``DIB_DNF_MODULE_STREAMS='virt:8.2 container-tools:3.0'``
