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
    elif [[ "${DISTRO_NAME}" == "opensuse" ]]; then
        export DIB_DISTRIBUTION_MIRROR=$NODEPOOL_OPENSUSE_MIRROR
    fi

fi

# This is repo files pre-created for the fedora/centos-minimal jobs in
# the gate
if [[ -d ${WORKSPACE:-/not/a/path/}/dib-mirror ]]; then

    if [[ "${DISTRO_NAME}" == "fedora" ]]; then
        export DIB_YUM_MINIMAL_BOOTSTRAP_REPOS=${WORKSPACE}/dib-mirror/fedora-minimal/yum.repos.d
    elif [[ "${DISTRO_NAME}" == "centos" ]]; then
        export DIB_YUM_MINIMAL_BOOTSTRAP_REPOS=${WORKSPACE}/dib-mirror/centos-minimal/yum.repos.d
    fi

fi
