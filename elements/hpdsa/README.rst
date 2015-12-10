=====
hpdsa
=====
This is the hpdsa element.

This element enables the 'hpdsa' driver to be included in
the ramdisk when invoked during ramdisk/image creation.

This driver is required for deploying the HP Proliant Servers
Gen9 with Dynamic Smart Array Controllers.

Note: This element supports only Ubuntu image/ramdisk to be
updated with the hpdsa driver. It installs hp certificate
from https://downloads.linux.hp.com/SDR/hpPublicKey2048_key1.pub.
Since HP has released this currently only for trusty,
It has been restricted to work only for trusty.
