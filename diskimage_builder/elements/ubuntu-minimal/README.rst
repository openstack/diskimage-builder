==============
ubuntu-minimal
==============

The ``ubuntu-minimal`` element uses debootstrap for generating a
minimal image. In contrast the ``ubuntu`` element uses the cloud-image
as the initial base.

.. note::

   You will need to install a working debootstrap for diskimage-builder. The
   version you install may not support all Debian and Ubuntu releases that you
   want to bootstrap. Consider using the zuul/nodepool-builder docker image
   instead as maximum compatibility is attempted there.

By default this element creates the latest LTS release.  The exact setting can
be found in the `ubuntu-common <https://docs.openstack.org/diskimage-builder/latest/elements/ubuntu-common/README.html>`_
element's ``environment.d`` directory in the variable ``DIB_RELEASE``.  If a
different release of Ubuntu should be created, the variable ``DIB_RELEASE`` can
be set appropriately.

Note that this element installs ``systemd-sysv`` as the init system for
18.04+.

Environment Variables
---------------------

DIB_UBUNTU_KERNEL:
  :Required: No
  :Default: ``linux-image-generic``
  :Description: Specifies the kernel meta package to install in the image.
  :Example: ``DIB_UBUNTU_KERNEL=linux-image-kvm``
  :Options: ``linux-image-generic``, ``linux-image-kvm``,
            ``linux-image-virtual``
  :Notes: The element must know about the package, otherwise it will select
          the default.


DIB_UBUNTU_MIRROR_DISTS:
  :Required: No
  :Default: ``updates,security,backports``
  :Description:  Allow to manage 'dists' repos
  :Example: ``DIB_UBUNTU_MIRROR_DISTS=updates,security``
  :Notes: For some deployment,
          is may be required to disable backport|update|etc packages integration.

.. element_deps::
