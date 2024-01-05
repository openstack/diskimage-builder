export DISTRO_NAME=opensuse
export DIB_RELEASE=${DIB_RELEASE:-15.5}
export EFI_BOOT_DIR="EFI/opensuse"
export DIB_OPENSUSE_PATTERNS=patterns-openSUSE-base
export DIB_INIT_SYSTEM=systemd
case ${DIB_RELEASE} in
    15.5) export OPENSUSE_REPO_DIR=openSUSE_Leap_${DIB_RELEASE} ;;
    *) echo "Unsupported openSUSE release: ${DIB_RELEASE}"; exit 1 ;;
esac

export DIB_DISTRIBUTION_MIRROR=${DIB_DISTRIBUTION_MIRROR:-https://download.opensuse.org}
