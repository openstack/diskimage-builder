export DISTRO_NAME=opensuse
export DIB_RELEASE=${DIB_RELEASE:-42.3}
export DIB_OPENSUSE_PATTERNS=patterns-openSUSE-base
case ${DIB_RELEASE} in
    # Old openSUSE releases
    13*) export OPENSUSE_REPO_DIR=openSUSE_${DIB_RELEASE} ;;
    # New Leap releases
    42*) export OPENSUSE_REPO_DIR=openSUSE_Leap_${DIB_RELEASE} ;;
    *) echo "Unsupported openSUSE release: ${DIB_RELEASE}"; exit 1 ;;
esac

export DIB_DISTRIBUTION_MIRROR=${DIB_DISTRIBUTION_MIRROR:-http://download.opensuse.org}
