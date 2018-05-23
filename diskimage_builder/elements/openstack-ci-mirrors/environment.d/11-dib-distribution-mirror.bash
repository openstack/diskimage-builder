# Set DIB_DISTRIBUTION_MIRROR and related if running in openstack gate

# don't spam logs with this source
_xtrace=$(set +o | grep xtrace)
set +o xtrace

if [ -f /etc/ci/mirror_info.sh ]; then
    # outside chroot
    mirror_info=/etc/ci/mirror_info.sh
elif [ -f /tmp/in_target.d/mirror_info.sh ]; then
    # inside chroot
    mirror_info=/tmp/in_target.d/mirror_info.sh
else
    echo "No mirror file found.  Not an OpenStack CI node?"
    return 0
fi

source $mirror_info
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
    export DIB_EPEL_MIRROR=$NODEPOOL_EPEL_MIRROR
elif [[ "${DISTRO_NAME}" == "centos7" ]]; then
    export DIB_DISTRIBUTION_MIRROR=$NODEPOOL_CENTOS_MIRROR
    export DIB_EPEL_MIRROR=$NODEPOOL_EPEL_MIRROR
elif [[ "${DISTRO_NAME}" == "opensuse" ]]; then
    export DIB_DISTRIBUTION_MIRROR=$NODEPOOL_OPENSUSE_MIRROR
fi

# Infra doesn't mirror non-free repos, so instruct to ignore these
export DIB_DISTRIBUTION_MIRROR_UBUNTU_IGNORE="(universe|multiverse)"
export DIB_DISTRIBUTION_MIRROR_UBUNTU_INSECURE=1

# These repo files are pre-created for the fedora/centos-minimal jobs
# in the gate.  Not relevant inside the chroot.
if [[ -d ${DIB_OS_CI_YUM_REPOS:-/not/a/path/} ]]; then

    if [[ "${DISTRO_NAME}" == "fedora" ]]; then
        if [[ -d ${DIB_OS_CI_YUM_REPOS}/fedora-minimal/${DIB_RELEASE} ]]; then
            export DIB_YUM_MINIMAL_BOOTSTRAP_REPOS=${DIB_OS_CI_YUM_REPOS}/fedora-minimal/${DIB_RELEASE}/yum.repos.d
        else
            export DIB_YUM_MINIMAL_BOOTSTRAP_REPOS=${DIB_OS_CI_YUM_REPOS}/fedora-minimal/default/yum.repos.d
        fi
    elif [[ "${DISTRO_NAME}" == "centos" ]]; then
        export DIB_YUM_MINIMAL_BOOTSTRAP_REPOS=${DIB_OS_CI_YUM_REPOS}/centos-minimal/yum.repos.d
    fi

fi

