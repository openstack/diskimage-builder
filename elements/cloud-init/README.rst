==========
cloud-init
==========

Install's and enables cloud-init for systems that don't come with it
pre-installed

Currently only supports Gentoo.

Environment Variables
---------------------

DIB_CLOUD_INIT_ALLOW_SSH_PWAUTH
  :Required: No
  :Default: password authentication disabled when cloud-init installed
  :Description: customize cloud-init to allow ssh password
    authentication.
