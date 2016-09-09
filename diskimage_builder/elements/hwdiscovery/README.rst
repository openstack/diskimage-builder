===========
hwdiscovery
===========
A ramdisk to report the hardware of a machine to an inventory service.

This will collect up some basic information about the hardware it 
boots on:

 * CPU cores
 * RAM
 * Disk
 * NIC mac address

This information will then be collated into a JSON document, base64 
encoded and passed, via HTTP POST, to a URL that you must specify on 
the kernel commandline, thus:

HW_DISCOVERY_URL=http://1.2.3.4:56/hw_script.asp


This is currently fairly fragile as there can be a huge variability in 
the number of disks/NICs in servers and how they are configured.

If other elements wish to inject data into the hardware discovery data, 
they can - they should be specified before hwdiscovery to the image 
building script, and they should contain something like this in their 
init fragment:

_vendor_hwdiscovery_data="$_vendor_hwdiscovery_data
 \"some vendor key\" : \"some data you care about\",
 \"some other vendor key\" : \"some other data you care about\","

Note that you are essentially feeding JSON into the main hwdiscovery 
JSON.

This will allow any number of vendor specific hwdiscovery elements to 
chain together their JSON fragments and maintain consistency.

