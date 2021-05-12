=============
containerfile
=============

Base element for creating images from container files (aka
Dockerfiles).

Usually this element will be called via a more specific distro element
which provides an environment for building a full image.  This element
will search active elements for a container file located in
`containerfiles/${DIB_RELEASE}`.

Alternatively, to use this element directly supply the path to a
container file in the environment variable `DIB_CONTAINER_FILE`.
