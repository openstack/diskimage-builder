==================
pip-and-virtualenv
==================

This element installs pip and virtualenv in the image.

Package install
===============

If the package installtype is used then these programs are installed
from distribution packages.  In this case, ``pip`` and ``virtualenv``
will be installed *only* for the python version identified by
``dib-python`` (i.e. the default python for the platform).

Namespacing of the tools will be up to your distribution.  Some
distribution packages have worked out name-spacing such that only
python2 or python3 owns common scripts like ``/usr/bin/pip`` (on most
platforms, ``pip`` refers to python2 pip, and ``pip3`` refers to
python3 pip, although some may choose the reverse).  Other platforms
have avoided making a decision and require explicit version suffixes.

To install pip and virtualenv from package::

  export DIB_INSTALLTYPE_pip_and_virtualenv=package

Source install
==============

.. note:: For source installs this element setups and Python 2 and
          Python 3 environments.  This means it will bring in python2
          packages, so isn't appropriate if you want a python3 only
          environment.

.. note:: Source install is considered deprecated for several reasons.
          Because it makes for a hetrogenous environment between
          distro packaged tools and upstream it means the final images
          create bespoke environments that make standarised testing
          difficult.  The tricks used around holding packages to
          overwrite them cause difficulty for users of images.  This
          also brings in Python 2 unconditonally, something not wanted
          on modern Python 3 only distributions.

Source install is the default on most platforms for historical
purposes.  The current exception(s) are RHEL8 and CentOS 8.

If the source installtype is used, ``pip`` and ``virtualenv`` are
installed from the latest upstream releases.

Source installs from upstream releases are not name-spaced.  It is
inconsistent across platforms if the first or last install will own
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

Environment Variables
=====================

To simplify the common-case of "install a package" or "create a
virtualenv" with the default system Python, the following variables
are exported by this element:

* ``DIB_PYTHON_PIP``
* ``DIB_PYTHON_VIRTUALENV``

This will create/install using the ``dib-python`` version for the
platform (i.e. python2 for older distros, python3 for modern distros).
Note that on Python 3 platforms it will use the inbuilt ``venv``
(rather than the ``virtualenv`` package -- if you absolutely need
features only ``virtualenv`` provides you should call it directly in
your element; see below).

Explicit use of the tools
=========================

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
