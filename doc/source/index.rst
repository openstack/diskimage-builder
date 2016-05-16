Diskimage-builder Documentation
===============================

``diskimage-builder`` is a tool for automatically building customized
operating-system images for use in clouds and other environments.

It includes support for building images based on many major
distributions and can produce cloud-images in all common formats
(``qcow2``, ``vhd``, ``raw``, etc), bare metal file-system images and
ram-disk images.  These images are composed from the many included
`elements`; ``diskimage-builder`` acts as a framework to easily add
your own elements for even further customization.

``diskimage-builder`` is used extensively by the `TripleO project
<https://wiki.openstack.org/wiki/TripleO>`__ and within `OpenStack
Infrastructure <http://docs.openstack.org/infra/system-config/>`__.

Code
----

Release notes for the latest and previous versions are available at:

 * `http://docs.openstack.org/releasenotes/diskimage-builder/
   <http://docs.openstack.org/releasenotes/diskimage-builder/>`__


The code is available at:

 * `https://git.openstack.org/cgit/openstack/diskimage-builder/
   <https://git.openstack.org/cgit/openstack/diskimage-builder/>`__


Table of Contents
-----------------

.. toctree::
   :maxdepth: 2

   user_guide/index
   developer/index
   elements
   copyright
