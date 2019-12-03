==============
zypper-minimal
==============
Base element for creating minimal SUSE-based images

This element is incomplete by itself so you probably want to use it along
with the opensuse-minimal one. It requires 'zypper' to be installed on the
host.

To create a zypper-based image with non-default repositories, set
``DIB_ZYPPER_REPOS`` to a mapping of repository names to URLs, for example::

  DIB_ZYPPER_REPOS="update=>http://smt-mirror.example.com/SUSE:/SLE-15-SP1:/Update/standard/ "
  DIB_ZYPPER_REPOS+="SLE-15-SP1=>http://smt-mirror.example.com/ibs/SUSE:/SLE-15-SP1:/GA/standard/ "
  DIB_ZYPPER_REPOS+="SLE-15=>http://smt-mirror.example.com/ibs/SUSE:/SLE-15:/GA/standard/ "
