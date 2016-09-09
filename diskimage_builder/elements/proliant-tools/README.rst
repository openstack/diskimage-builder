proliant-tools
==============

* This element can be used when building ironic-agent ramdisk.  It
  enables ironic-agent ramdisk to do in-band cleaning operations specific
  to HP ProLiant hardware.

* Works with ubuntu and fedora distributions (on which ironic-agent
  element is supported).

* Currently the following utilities are installed:

  + `proliantutils`_ - This module registers an ironic-python-agent hardware
    manager for HP ProLiant hardware, which implements in-band cleaning
    steps.  The latest version of ``proliantutils`` available is
    installed.  This python module is released with Apache license.

  + `HP Smart Storage Administrator (HP SSA) CLI for Linux 64-bit`_ - This
    utility is used by ``proliantutils`` library above for doing in-band RAID
    configuration on HP ProLiant hardware.  Currently installed version is
    2.30.  Newer version of ``hpssacli`` when available, may be installed to
    the ramdisk by using the environment variable ``DIB_HPSSACLI_URL``.
    ``DIB_HPSSACLI_URL`` should contain the HTTP(S) URL for downloading the
    RPM package for ``hpssacli`` utility.  Availability of newer versions can
    be in the Revision History in the above link.  This utility is closed source
    and is released with `HP End User License Agreement – Enterprise Version`_.

.. _`proliantutils`: https://pypi.python.org/pypi/proliantutils
.. _`HP Smart Storage Administrator (HP SSA) CLI for Linux 64-bit`: http://h20564.www2.hpe.com/hpsc/swd/public/detail?swItemId=MTX_b6a6acb9762443b182280db805
.. _`HP End User License Agreement – Enterprise Version`: ftp://ftp.hp.com/pub/softlib2/software1/doc/p2057331991/v33194/hpeula-en.html
