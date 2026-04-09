# DISTRO_NAME and DIB_RELEASE must be set by the caller since the tarball
# element does not know what OS is contained in the tarball.
# For example:
#   export DISTRO_NAME=ubuntu
#   export DIB_RELEASE=noble
export DISTRO_NAME=${DISTRO_NAME:-tarball}
export DIB_RELEASE=${DIB_RELEASE:-unknown}
