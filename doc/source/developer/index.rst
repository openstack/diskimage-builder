Developer Documentation
=======================

This documentation explains how to get started with creating your own
disk-image-builder elements as well as some high level concepts for element
creation.

Quickstart
----------

To get started developing with ``diskimage-builder``, install to a
``virtualenv``::

 $ mkdir dib
 $ cd dib
 $ virtualenv create env
 $ source env/bin/activate
 $ git clone https://git.openstack.org/openstack/diskimage-builder
 $ cd diskimage-builder
 $ pip install -e .

You can now simply use ``disk-image-create`` to start building images
and testing your changes.  When you are done editing, use ``git
review`` to submit changes to the upstream gerrit.


.. toctree::
   :maxdepth: 2

   design
   components
   invocation
   caches
   developing_elements
   dib_lint
   stable_interfaces
