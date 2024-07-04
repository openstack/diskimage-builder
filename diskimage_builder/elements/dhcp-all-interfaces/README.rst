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

Environment Variables
---------------------

DIB_DHCP_TIMEOUT
  :Required: No
  :Default: 30
  :Description: Amount of time in seconds that the systemd service(or dhclient)
   will wait to get an address. Should be increased in networks such as
   Infiniband.
  :Example: DIB_DHCP_TIMEOUT=300

DIB_DHCP_NETWORK_MANAGER_AUTO
  :Required: No
  :Default: false
  :Description: When NetworkManager is detected, and this is set to true the
   dhcp-all-interfaces service will not be installed. Only the NetworkManager
   configuration will be added. NetworkManager is quite capable to do automatic
   interface configuration. NetworkManager will by default try to
   auto-configure any interface with no configuration, it will use DHCP for
   IPv4 and Router Advertisements to decide how to initialize IPv6.
  :Example: DIB_DHCP_NETWORK_MANAGER_AUTO=true

DIB_DHCP_CLIENT
  :Required: no
  :Default: internal
  :Description: When NetworkManager is in use, this setting conveys which DHCP
   client is in use for acquiring a DHCP address for the node. In some specific
   cases, where known that dhclient is the tested or most compatible default,
   specifically for Centos 8, and 8-Stream, as well as derived distributions.
   Otherwise, the "internal" dhcp client is the default.
  :Example: DIB_DHCP_CLIENT
