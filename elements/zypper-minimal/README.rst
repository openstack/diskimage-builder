==============
zypper-minimal
==============
Base element for creating minimal SUSE-based images

This element is incomplete by itself so you probaby want to use it along
with the opensuse-minimal one. It requires 'zypper' to be installed on the
host.

Repositories
------------

This element expects the `ZYPPER_REPOS` variable to be exported by the
operating system element. This variable contains repository mappings in 
the following format: `${repo_name}==>${repo_url}`. For example::

 ZYPPER_REPOS="update=>http://download.opensuse.org/update/leap/42.1/oss/ "
 ZYPPER_REPOS+="oss=>http://download.opensuse.org/distribution/leap/42.1/repo/oss/"
 export ZYPPER_REPOS
