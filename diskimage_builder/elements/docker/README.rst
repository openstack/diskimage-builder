======
docker
======

Base element for creating images from docker containers.

This element is incomplete by itself, you'll want to add additional elements,
such as dpkg or yum to get richer features. At its heart, this element simply
exports a root tarball from a named docker container so that other
diskimage-builder elements can build on top of it.

The variables `DISTRO_NAME` and `DIB_RELEASE` will be used to decide which
docker image to pull, and are required for most other elements. Additionally,
the `DIB_DOCKER_IMAGE` environment variable can be set in addition to
`DISTRO_NAME` and `DIB_RELEASE` if a different docker image is desired.
