if [ -z "${DISTRO_NAME:-}" ]; then
    echo "DISTRO_NAME is not set! Can not continue"
    exit 1
fi
if [ -z "${DIB_RELEASE:-}" ]; then
    echo "DIB_RELEASE is not set! Can not continue"
    exit 1
fi
if [ -z "${EFI_BOOT_DIR:-}" ]; then
    echo "EFI_BOOT_DIR is not set! Can not continue"
    exit 1
fi
if [ -z "${DIB_INIT_SYSTEM:-}" ]; then
    echo "DIB_INIT_SYSTEM is not set! Can not continue"
    exit 1
fi
if [ -z "${DIB_BLOCK_DEVICE:-}" ]; then
    echo "DIB_BLOCK_DEVICE is not set! Can not continue"
    exit 1
fi
export DIB_SKIP_GRUB_PACKAGE_INSTALL=True
export DIB_SKIP_BASE_PACKAGE_INSTALL=1
export DIB_AVOID_PACKAGES_UPDATE=1
export DIB_IMAGE_EXTRACT_GUESTFISH=True
export DIB_SOURCE_BLOCK_SIZE=512
