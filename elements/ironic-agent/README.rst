============
ironic-agent
============
Builds a ramdisk with ironic-python-agent.  More information can be found at:
    https://git.openstack.org/cgit/openstack/ironic-python-agent/

Beyond installing the ironic-python-agent, this element does the following:

* Installs the ``dhcp-all-interfaces`` so the node, upon booting, attempts to
  obtain an IP address on all available network interfaces.
* Disables the ``iptables`` service on SysV and systemd based systems.
* Disables the ``ufw`` service on Upstart based systems.
* Installs packages required for the operation of the ironic-python-agent::
    ``qemu-utils`` ``parted`` ``hdparm`` ``util-linux`` ``genisoimage``
* When installing from source, ``python-dev`` and ``gcc`` are also installed
  in order to support source based installation of ironic-python-agent and its
  dependencies.

.. note::
   The package based install currently only enables the service when using the
   systemd init system. This can easily be changed if there is an agent
   package which includes upstart or sysv packaging.

.. note::
   Using the ramdisk will require at least 1.5GB of ram
