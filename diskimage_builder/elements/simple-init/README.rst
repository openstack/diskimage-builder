===========
simple-init
===========
Basic network and system configuration that can't be done until boot

Unfortunately, as much as we'd like to bake it in to an image, we can't
know in advance how many network devices will be present, nor if DHCP is
present in the host cloud. Additionally, in environments where cloud-init
is not used, there are a couple of small things, like mounting config-drive
and pulling ssh keys from it, that need to be done at boot time.

Autodetect network interfaces during boot and configure them
------------------------------------------------------------

The rationale for this is that we are likely to require multiple
network interfaces for use cases such as baremetal and there is no way
to know ahead of time which one is which, so we will simply run a
DHCP client on all interfaces with real MAC addresses (except lo) that
are visible on the first boot.

The script `/usr/local/sbin/simple-init.sh` will be called
early in each boot and will scan available network interfaces and
ensure they are configured properly before networking services are started.

Processing startup information from config-drive
------------------------------------------------

On most systems, the DHCP approach desribed above is fine. But in some clouds,
such as Rackspace Public cloud, there is no DHCP.  Instead, there is static
network config via `config-drive`. `simple-init` will happily call
`glean` which will do nothing if static network information is
not there.

Finally, glean will handle ssh-keypair-injection from config
drive if cloud-init is not installed.

Chosing glean installation source
---------------------------------

By default glean is installed using pip using the latest release on pypi.
It is also possible to install glean from a specified git repository
location. This is useful for debugging and testing new glean changes
for example. To do this you need to set these variables::

  DIB_INSTALLTYPE_simple_init=repo
  DIB_REPOLOCATION_glean=/path/to/glean/repo
  DIB_REPOREF_glean=name_of_git_ref

For example to test glean change 364516 do::

  git clone https://git.openstack.org/openstack-infra/glean /tmp/glean
  cd /tmp/glean
  git review -d 364516
  git checkout -b my-test-ref

Then set your DIB env vars like this before running DIB::

  DIB_INSTALLTYPE_simple_init=repo
  DIB_REPOLOCATION_glean=/tmp/glean
  DIB_REPOREF_glean=my-test-ref
