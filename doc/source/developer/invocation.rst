Developer Installation
======================

Note that for non-development use you can use distribution packages or
install the latest release via ``pip`` in a ``virtualenv``.

For development purposes, you can use ``pip -e`` to install the latest
git tree checkout into a local development/testing ``virtualenv``, or
use ``tox -e venv -- disk-image-create`` to run within a ``tox``
created environment.

For example, to create a ``virtualenv`` and install

::

   $ mkdir dib
   $ cd dib
   $ virtualenv env
   $ source env/bin/activate
   $ git clone https://git.openstack.org/openstack/diskimage-builder
   $ cd diskimage-builder
   $ pip install -e .

Invocation
==========

The scripts can generally just be run. Options can be set on the
command line or by exporting variables to override those present in
lib/img-defaults. -h to get help.

The image building scripts expect to be able to invoke commands with
sudo, so if you want them to run non-interactively, you should either
run them as root, with sudo -E, or allow your build user to run any
sudo command without password.

The variable ``ELEMENTS_PATH`` is a colon (:) separated path list to
search for elements.  The included ``elements`` tree is used when no
path is supplied and is always added to the end of the path if a path
is supplied.  Earlier elements will override later elements, i.e. with
``ELEMENTS_PATH=foo:bar`` the element ``my-element`` will be chosen
from ``foo/my-element`` over ``bar/my-element``, or any in-built
element of the same name.

By default, the image building scripts will not overwrite existing
disk images, allowing you to compare the newly built image with the
existing one. To change that behaviour, set the variable
``OVERWRITE_OLD_IMAGE`` to any value that isn't ``0``. If this value is
zero then any existing image will be moved before the new image is
written to the destination.

Setting the variable ``DIB_SHOW_IMAGE_USAGE`` will print out a
summarised disk-usage report for the final image of files and
directories over 10MiB in size.  Setting ``DIB_SHOW_IMAGE_USAGE_FULL``
will show all files and directories.  These settings can be useful
additions to the logs in automated build situations where debugging
image-growth may be important.
