export DISTRO_NAME=opensuse
DIB_RELEASE=${DIB_RELEASE:-42.2}
export DIB_RELEASE=${DIB_RELEASE,,}
export DIB_OPENSUSE_MIRROR=${DIB_OPENSUSE_MIRROR:-http://download.opensuse.org}
case ${DIB_RELEASE} in
    # We are using "=>" as the assignment symbol since "@" "=" etc could be used in the URI itself.
    # Remember, we can't export an array in bash so we use a string instead.
    # Repo format: {name}=>{uri}
    # Old openSUSE releases
    13*)
        ZYPPER_REPOS="update=>${DIB_OPENSUSE_MIRROR}/update/${DIB_RELEASE}/ "
        ZYPPER_REPOS+="oss=>${DIB_OPENSUSE_MIRROR}/distribution/${DIB_RELEASE}/repo/oss/"
        ;;
    # New Leap releases
    42*)
        ZYPPER_REPOS="update=>${DIB_OPENSUSE_MIRROR}/update/leap/${DIB_RELEASE}/oss/ "
        ZYPPER_REPOS+="oss=>${DIB_OPENSUSE_MIRROR}/distribution/leap/${DIB_RELEASE}/repo/oss/"
        ;;
    # Tumbleweed
    tumbleweed)
        ZYPPER_REPOS="update=>${DIB_OPENSUSE_MIRROR}/update/${DIB_RELEASE}/ "
        ZYPPER_REPOS+="oss=>${DIB_OPENSUSE_MIRROR}/${DIB_RELEASE}/repo/oss/"
        ;;
    *) echo "Unsupported openSUSE release: ${DIB_RELEASE}"; exit 1 ;;
esac
export ZYPPER_REPOS
