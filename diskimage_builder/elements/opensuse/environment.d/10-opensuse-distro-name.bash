export DISTRO_NAME=opensuse
export DIB_RELEASE=${DIB_RELEASE:-15.0}
export DIB_OPENSUSE_PATTERNS=patterns-openSUSE-base
case ${DIB_RELEASE} in
    # Old Leap releases
    42*) export OPENSUSE_REPO_DIR=openSUSE_Leap_${DIB_RELEASE} ;;
    # New Leap releases
    15*) export OPENSUSE_REPO_DIR=openSUSE_Leap_${DIB_RELEASE} ;;
    *) echo "Unsupported openSUSE release: ${DIB_RELEASE}"; exit 1 ;;
esac

export DIB_DISTRIBUTION_MIRROR=${DIB_DISTRIBUTION_MIRROR:-https://download.opensuse.org}
