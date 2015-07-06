Stable Interfaces
=================

diskimage-builder and the elements provide several 'stable' interfaces for both
developers and users which we aim to preserve during a major version release.
These interfaces consist of:

The names and arguments of the executable scripts included with
diskimage-builder in the bin directory will remain stable.

The environment variables that diskimage-builder provides for elements to use
will remain stable.

The environment variables documented in each element and the values accepted
by these environment variables will remain stable.

Required environment variables for an element will not be added.

Support for build or target distributions will not be removed.
