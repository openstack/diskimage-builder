Caches and offline mode
=======================

Since retrieving and transforming operating system image files, git
repositories, Python or Ruby packages, and so on can be a significant overhead,
we cache many of the inputs to the build process in ~/.cache/image-create/. The
writing an element documention describes the interface within
disk-image-builder for caching. When invoking disk-image-builder the --offline
option will instruct disk-image-builder to not refresh cached resources.

Note that we don't maintain operating system package caches, instead depending
on your local infrastructure (e.g. Squid cache, or an APT or Yum proxy) to
facilitate caching of that layer, so you need to arrange independently for
offline mode.

Base images
-----------

These are cached by the standard elements - fedora, redhat, ubuntu,
debian and opensuse.

source-repositories
-------------------

Git repositories and tarballs obtained via the source-repositories element will
be cached.

C and C++ compilation
---------------------

Ccache is configured by the base element. Any compilation that honours ccache
will be cached.

PyPI
----

The pypi element will bind mount a PyPI mirror from the cache dir and configure
pip and easy-install to use it.
