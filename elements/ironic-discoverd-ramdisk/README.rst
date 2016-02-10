========================
ironic-discoverd-ramdisk
========================

.. warning::
   This element is deprecated.  Please use the ironic-agent element
   instead.

ironic-inspector [1] is a project for conducting hardware properties
discovery via booting a special ramdisk and interrogating hardware
from within it.

This ramdisk collects hardware information from the machine
it's booted on and posts it to the URL provided via
kernel argument 'discoverd_callback_url'.

The hardware information collected by the ramdisk are:

* BMC IP address (may be required for associating with existing node in Ironic)
* CPU count and architecture
* Memory amount in MiB
* Hard drive size in GiB
* IP and mac addresses for all NICs except the loopback

The machine is halted at the end of the process.

[1] https://pypi.python.org/pypi/ironic-inspector
