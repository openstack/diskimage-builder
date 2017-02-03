export DISTRO_NAME=centos7
export DIB_RELEASE=GenericCloud

# Useful for elements that work with fedora (dnf) & centos
export YUM=${YUM:-yum}

if [ -n "${DIB_CENTOS_DISTRIBUTION_MIRROR:-}" ]; then
    export DIB_DISTRIBUTION_MIRROR=$DIB_CENTOS_DISTRIBUTION_MIRROR
fi
