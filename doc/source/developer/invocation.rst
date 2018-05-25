.. _dev_install:

Developer Installation
======================

Note that for non-development use you can use distribution packages or
install the latest release via ``pip`` (usually in a separate
``virtualenv`` environment).

For development purposes, you can use ``pip -e`` to install the latest
git tree checkout into a local development/testing ``virtualenv``.

However, the recommended way is to use provided ``tox`` environments;
e.g.

.. code-block:: shell-session

   $ git clone https://git.openstack.org/openstack/diskimage-builder
   $ cd diskimage-builder

   $ tox -e bindep
   $ sudo apt-get install <any-missing-packages-from-bindep>

   $ tox -e venv -- disk-image-create ...

This will ensure you run with the right requirements.

Invocation
----------

The ``image-create`` scripts should be run from the ``$PATH``; this
should will be automatically set if using a ``virtualenv`` or ``tox``.

A range of options can be set on the command-line.  Try ``-h`` for
help.

Other options can be set by exporting variables; some variables for
export are listed in ``lib/img-defaults``.  See specific element
instructions for other variables that may be obeyed.

The image building scripts expect to be able to invoke commands with
``sudo``.  Thus if you want them to run non-interactively, you should
either run them as root, with ``sudo -E``, or allow your build user to
run any ``sudo`` command without password.

Element priority
----------------

The variable ``ELEMENTS_PATH`` is a colon (:) separated path list to
search for elements.  The included ``elements`` tree is used when no
path is supplied and is always added to the end of the path if a path
is supplied.  Earlier elements will override later elements, i.e. with
``ELEMENTS_PATH=foo:bar`` the element ``my-element`` will be chosen
from ``foo/my-element`` over ``bar/my-element``, or any in-built
element of the same name.

Output
------

By default, the image building scripts will not overwrite existing
disk images, allowing you to compare the newly built image with the
existing one. To change that behaviour, set the variable
``OVERWRITE_OLD_IMAGE`` to any value that isn't ``0``. If this value is
zero then any existing image will be moved before the new image is
written to the destination.

Size reports
------------

Setting the variable ``DIB_SHOW_IMAGE_USAGE`` will print out a
summarised disk-usage report for the final image of files and
directories over 10MiB in size.  Setting ``DIB_SHOW_IMAGE_USAGE_FULL``
will show all files and directories.  These settings can be useful
additions to the logs in automated build situations where debugging
image-growth may be important.
