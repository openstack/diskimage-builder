=============
containerfile
=============

Base element for creating images from container files (aka
Dockerfiles).

Usually this element will be called via a more specific distro element
which provides an environment for building a full image.  This element
will search active elements for a container file located in
``containerfiles/${DIB_RELEASE}``.

Alternatively, to use this element directly supply the path to a
container file in the environment variable
``DIB_CONTAINERFILE_DOCKERFILE``.

Set ``DIB_CONTAINERFILE_RUNTIME`` to ``docker`` to use Docker for building
images (default is ``podman``).

Set ``DIB_CONTAINERFILE_RUNTIME_ROOT`` to ``1`` to run the runtime
(Docker or ``podman``, per above) as ``root``.

Set ``DIB_CONTAINERFILE_NETWORK_DRIVER`` to a network driver of your choice
(e.g. host) to use it instead of the default bridge during build.

Set ``DIB_CONTAINERFILE_BUILDOPTS`` to pass any other options to build command, e.g. ``--from docker.io/library/ubuntu:jammy --build-arg=HTTP_PROXY=http://10.20.30.2:1234``
