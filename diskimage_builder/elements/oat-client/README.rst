==========
oat-client
==========
This element installs oat-client on the image, that's necessary for
trusted boot feature in Ironic to work.

Intel TXT will measure BIOS, Option Rom and Kernel/Ramdisk during trusted
boot, the oat-client will securely fetch the hash values from TPM.

.. note::
    This element only works on Fedora.

Put `fedora-oat.repo` into `/etc/yum.repos.d/`::

  export DIB_YUM_REPO_CONF=/etc/yum.repos.d/fedora-oat.repo

.. note::
    OAT Repo is lack of a GPG signature check on packages, which can be
    tracked on: https://github.com/OpenAttestation/OpenAttestation/issues/26
