Caches and offline mode
=======================

Since retrieving and transforming operating system image files, git
repositories, Python or Ruby packages, and so on can be a significant overhead,
we cache many of the inputs to the build process.

The cache location is read from ``DIB_IMAGE_CACHE``. :ref:`developing-elements`
describes the interface within disk-image-builder for caching.

When invoking disk-image-builder, the ``--offline`` option will instruct
disk-image-builder to not refresh cached resources. Alternatively you can set
``DIB_OFFLINE=1``.

Note that we don't maintain operating system package caches, instead depending
on your local infrastructure (e.g. Squid cache, or an APT or Yum proxy) to
facilitate caching of that layer, so you need to arrange independently for
offline mode. For more information about setting up a squid proxy, consult the
`TripleO documentation
<http://docs.openstack.org/developer/tripleo-incubator/devtest_setup.html#f3>`_.

Base images
-----------

These are cached by the standard elements - :doc:`../elements/fedora/README`,
:doc:`../elements/redhat-common/README`, :doc:`../elements/ubuntu/README`,
:doc:`../elements/debian/README` and :doc:`../elements/opensuse/README`.

source-repositories
-------------------

Git repositories and tarballs obtained via the
:doc:`../elements/source-repositories/README` element will be cached.

C and C++ compilation
---------------------

Ccache is configured by the :doc:`../elements/base/README` element. Any
compilation that honours ccache will be cached.

PyPI
----

The :doc:`../elements/pypi/README` element will bind mount a PyPI mirror from
the cache dir and configure pip and easy-install to use it.
