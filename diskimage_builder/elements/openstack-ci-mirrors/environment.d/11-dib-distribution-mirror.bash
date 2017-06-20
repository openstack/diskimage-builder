# Set DIB_DISTRIBUTION_MIRROR if running in openstack gate
if [ -f /etc/ci/mirror_info.sh ]; then

    # don't spam logs with this source
    _xtrace=$(set +o | grep xtrace)
    set +o xtrace
    source /etc/ci/mirror_info.sh
    $_xtrace

    # note 11- is after 10- which is where DISTRO_NAME is set usually

    if [[ "${DISTRO_NAME}" == "ubuntu" ]]; then
        export DIB_DISTRIBUTION_MIRROR=$NODEPOOL_UBUNTU_MIRROR
        export DIB_DEBOOTSTRAP_EXTRA_ARGS+=" --no-check-gpg"
    elif [[ "${DISTRO_NAME}" == "debian" ]]; then
        export DIB_DISTRIBUTION_MIRROR=$NODEPOOL_DEBIAN_MIRROR
        export DIB_DEBOOTSTRAP_EXTRA_ARGS+=" --no-check-gpg"
    elif [[ "${DISTRO_NAME}" == "fedora" ]]; then
        export DIB_DISTRIBUTION_MIRROR=$NODEPOOL_FEDORA_MIRROR
    elif [[ "${DISTRO_NAME}" == "centos" ]]; then
        export DIB_DISTRIBUTION_MIRROR=$NODEPOOL_CENTOS_MIRROR
    elif [[ "${DISTRO_NAME}" == "centos7" ]]; then
        export DIB_DISTRIBUTION_MIRROR=$NODEPOOL_CENTOS_MIRROR
    fi

fi
