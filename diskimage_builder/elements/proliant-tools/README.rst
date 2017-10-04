proliant-tools
==============

* This element can be used when building ironic-agent ramdisk.  It
  enables ironic-agent ramdisk to do in-band cleaning operations specific
  to HPE ProLiant hardware.

* Works with ubuntu and fedora distributions (on which ironic-agent
  element is supported).

* Currently the following utilities are installed:

  + `proliantutils`_ - This module registers an ironic-python-agent hardware
    manager for HPE ProLiant hardware, which implements in-band cleaning
    steps.  The latest version of ``proliantutils`` available is
    installed.  This python module is released with Apache license.

  + `HPE Smart Storage Administrator (HPE SSA) CLI for Linux 64-bit`_ - This
    utility is used by ``proliantutils`` library above for doing in-band RAID
    configuration on HPE ProLiant hardware.  Currently installed version is
    2.60.  Newer version of ``ssacli`` when available, may be installed to
    the ramdisk by using the environment variable ``DIB_SSACLI_URL``.
    ``DIB_SSACLI_URL`` should contain the HTTP(S) URL for downloading the
    RPM package for ``ssacli`` utility.  The old environmental variable
    ``DIB_HPSSACLI_URL``,a HTTP(S) URL for downloading the RPM package for
    ``hpssacli`` utility, is deprecated. The ``hpssacli`` utility is not
    supported anymore, use ``ssacli`` instead for the same functionality.
    Availability of newer versions can be in the Revision History
    in the above link.  This utility is closed source and is released with
    `HPE End User License Agreement – Enterprise Version`_.

.. _`proliantutils`: https://pypi.python.org/pypi/proliantutils
.. _`HPE Smart Storage Administrator (HPE SSA) CLI for Linux 64-bit`: http://h20564.www2.hpe.com/hpsc/swd/public/detail?swItemId=MTX_5530b3f5b38b4e0781e6bf9c74
.. _`HPE End User License Agreement – Enterprise Version`: https://downloads.hpe.com/pub/softlib2/software1/doc/p1796552785/v113125/eula-en.html
