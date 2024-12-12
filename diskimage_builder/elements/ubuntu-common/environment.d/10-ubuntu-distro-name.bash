export DISTRO_NAME=${DISTRO_NAME:-ubuntu}
export DIB_RELEASE=${DIB_RELEASE:-noble}
export DIB_DEBIAN_COMPONENTS=${DIB_DEBIAN_COMPONENTS:-main,universe}
export EFI_BOOT_DIR="EFI/ubuntu"

# There are two default distro mirrors depending on architecture
ARCH=${ARCH:-}
if [[ "arm64 armhf powerpc ppc64el s390x" =~ "$ARCH" ]]; then
    default_ubuntu_mirror=http://ports.ubuntu.com/ubuntu-ports
else
    default_ubuntu_mirror=http://archive.ubuntu.com/ubuntu
fi

export DIB_DISTRIBUTION_MIRROR=${DIB_DISTRIBUTION_MIRROR:-$default_ubuntu_mirror}
