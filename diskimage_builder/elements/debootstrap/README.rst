===========
debootstrap
===========

Base element for creating minimal debian-based images.

This element is incomplete by itself, you'll want to use elements like
debian-minimal or ubuntu-minimal to get an actual base image.

There are two ways to configure apt-sources:

1. Using the standard way of defining the default apt sources
   release, updates and security repositories is the default. In this
   case you can overwrite the two environment variables to adapt the
   behavior:

   * ``DIB_DISTRIBUTION_MIRROR``: the mirror to use (default:
     `<http://deb.debian.org/debian>`__)
   * ``DIB_DEBIAN_COMPONENTS``: (default: ``main``) a comma
     separated list of components. For Debian this can be
     e.g. ``main,contrib,non-free``.

   By default only the ``main`` component is used. If
   ``DIB_DEBIAN_COMPONENTS`` (comma separated) from the
   ``debootstrap`` element has been set, that list of components will
   be used instead.

   Updates and security are included unless ``DIB_RELEASE``
   is ``testing`` or ``unstable``. For these ``DIB_RELEASE`` values only
   the default release source is included.

2. Complete configuration given in the variable ``DIB_APT_SOURCES_CONF``.

   Each line contains exactly one entry for the sources.list.d
   directory.  The first word must be the logical name (which is used
   as file name with ``.list`` automatically appended), followed by a
   colon ``:``, followed by the complete repository specification.

   .. code-block:: bash

      DIB_APT_SOURCES_CONF=\
        "default:deb http://10.0.0.10/ stretch main contrib
         mysecurity:deb http://10.0.0.10/ stretch-security main contrib"

If necessary, a custom apt keyring and debootstrap script can be
supplied to the ``debootstrap`` command via ``DIB_APT_KEYRING`` and
``DIB_DEBIAN_DEBOOTSTRAP_SCRIPT`` respectively. Both options require the
use of absolute rather than relative paths.

Use of this element will also require the tool 'debootstrap' to be
available on your system. It should be available on Ubuntu, Debian,
and Fedora. It is also recommended that the 'debian-keyring' package
be installed.

The ``DIB_OFFLINE`` or more specific ``DIB_DEBIAN_USE_DEBOOTSTRAP_CACHE``
variables can be set to prefer the use of a pre-cached root filesystem
tarball.

The ``DIB_DEBOOTSTRAP_EXTRA_ARGS`` environment variable may be used to
pass extra arguments to the debootstrap command used to create the
base filesystem image. If --keyring is used in ``DIB_DEBOOTSTRAP_EXTRA_ARGS``,
it will override ``DIB_APT_KEYRING`` if that is used as well.

For further information about ``DIB_DEBIAN_DEBOOTSTRAP_SCRIPT`` ,
``DIB_DEBIAN_USE_DEBOOTSTRAP_CACHE`` and ``DIB_DEBOOTSTRAP_EXTRA_ARGS``
please consult "README.rst" of the debootstrap element.

.. note::

   The rules above primarily apply to the debian-minimal element. The
   ubuntu-minimal element uses different configuration vars for things
   like configuring apt sources and its defaults may differ.

----------
Networking
----------

By default ``/etc/network/interfaces.d/eth[0|1]`` files will be
created and enabled with DHCP networking.  If you do not wish this to
be done, set ``DIB_APT_MINIMAL_CREATE_INTERFACES`` to ``0``.  If you
need different interface names than ``eth[0|1]`` set
``DIB_NETWORK_INTERFACE_NAMES`` to a space separated list of network
interface names like:

.. code-block:: bash

   export DIB_NETWORK_INTERFACE_NAMES="ens3 ens4"

-------------------
Note on ARM systems
-------------------

Because there is not a one-to-one mapping of ``ARCH`` to a kernel package, if
you are building an image for ARM on debian, you need to specify which kernel
you want in the environment variable ``DIB_ARM_KERNEL``. For instance, if you want
the ``linux-image-mx5`` package installed, set ``DIB_ARM_KERNEL`` to ``mx5``.

.. element_deps::
