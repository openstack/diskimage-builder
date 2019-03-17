export DISTRO_NAME=rhel
export DIB_RELEASE=${DIB_RELEASE:-8}

if [ "${DISTRO_NAME}" = "rhel" ] && [ "${DIB_RELEASE}" = "8" ] && [ "${FS_TYPE}" != "xfs" ]; then
    echo "ERROR: RHEL8 images file-system type must be set to xfs, FS_TYPE is currently set to" $FS_TYPE
    exit 1
fi
