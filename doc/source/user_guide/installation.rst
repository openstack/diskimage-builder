Installation
============

If your distribution does not proivde packages, you should install
``diskimage-builder`` via ``pip``, mostly likely in a ``virtualenv``
to keep it separate.

For example, to create a ``virtualenv`` and install from ``pip``

::

   virtualenv ~/dib-virtualenv
   . ~/dib-virtualenv/bin/activate
   pip install diskimage-builder


Once installed, you will be able to :doc:`build images
<building_an_image>` using ``disk-image-create`` and the elements
included in the main ``diskimage-builder`` repository.


Requirements
------------

Most image formats require the ``qemu-img`` tool which is provided by
the ``qemu-utils`` package on Ubuntu/Debian or the ``qemu`` package on
Fedora/RHEL/opensuse/Gentoo.

When generating images with partitions, the ``kpartx`` tool is needed,
which is provided by the ``kpartx`` package.

Some image formats, such as ``VHD``, may require additional
tools. Please see the ``disk-image-create`` help output for more
information.

Individual elements can also have additional dependencies for the build host.
It is recommended you check the documentation for each element you are using
to determine if there are any additional dependencies. Of particular note is
the need for the `dev-python/pyyaml` package on Gentoo hosts.

Package Installation
--------------------

On Gentoo you can emerge diskimage-builder directly.

::

    emerge app-emulation/diskimage-builder

