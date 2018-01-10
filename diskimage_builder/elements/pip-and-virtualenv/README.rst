==================
pip-and-virtualenv
==================

This element installs pip and virtualenv in the image.

.. note:: This element setups and Python 2 and Python 3 environment.
          This means it will bring in python2 packages, so isn't
          appropriate if you want a python3 only environment.

Package install
===============

If the package installtype is used then these programs are installed
from distribution packages.  In this case, ``pip`` and ``virtualenv``
will be installed *only* for the python version identified by
``dib-python`` (i.e. the default python for the platform).

Distribution packages have worked out name-spacing such that only
python2 or python3 owns common scripts like ``/usr/bin/pip`` (on most
platforms, ``pip`` refers to python2 pip, and ``pip3`` refers to
python3 pip, although some may choose the reverse).

To install pip and virtualenv from package::

  export DIB_INSTALLTYPE_pip_and_virtualenv=package

Source install
==============

Source install is the default.  If the source installtype is used,
``pip`` and ``virtualenv`` are installed from the latest upstream
releases.

Source installs from these tools are not name-spaced.  It is
inconsistent across platforms if the first or last install gets to own
common scripts like ``/usr/bin/pip`` and ``virtualenv``.

To avoid inconsistency, we firstly install the packaged python 2
**and** 3 versions of ``pip`` and ``virtualenv``.  This prevents a
later install of these distribution packages conflicting with the
source install.  We then overwrite ``pip`` and ``virtualenv`` via
``get-pip.py`` and ``pip`` respectively.

The system will be left in the following state:

* ``/usr/bin/pip`` : python2 pip
* ``/usr/bin/pip2`` : python2 pip (same as prior)
* ``/usr/bin/pip3`` : python3 pip
* ``/usr/bin/virtualenv`` : python2 virtualenv

(note python3 ``virtualenv`` script is *not* installed, see below)

Source install is supported on limited platforms.  See the code, but
this includes Ubuntu and RedHat platforms.

Using the tools
===============

Due to the essentially unsolvable problem of "who owns the script", it
is recommended to *not* call ``pip`` or ``virtualenv`` directly.  You
can directly call them with the ``-m`` argument to the python
interpreter you wish to install with.

For example, to create a python3 environment do::

  # python3 -m virtualenv myenv
  # myenv/bin/pip install mytool

To install a python2 tool from pip::

  # python2 -m pip install mytool

In this way, you can always know which interpreter is being used (and
affected by) the call.

Ordering
========
Any element that uses these commands must be designated as
05-* or higher to ensure that they are first installed.
