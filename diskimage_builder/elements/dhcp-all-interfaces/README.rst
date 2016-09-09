===================
dhcp-all-interfaces
===================
Autodetect network interfaces during boot and configure them for DHCP

The rationale for this is that we are likely to require multiple
network interfaces for use cases such as baremetal and there is no way
to know ahead of time which one is which, so we will simply run a
DHCP client on all interfaces with real MAC addresses (except lo) that
are visible on the first boot.

On non-Gentoo based distributions the script
/usr/local/sbin/dhcp-all-interfaces.sh will be called early in each
boot and will scan available network interfaces and ensure they are
configured properly before networking services are started.

On Gentoo based distributions we will install the dhcpcd package and
ensure the service starts at boot.  This service automatically sets
up all interfaces found via dhcp and/or dhcpv6 (or SLAAC).
