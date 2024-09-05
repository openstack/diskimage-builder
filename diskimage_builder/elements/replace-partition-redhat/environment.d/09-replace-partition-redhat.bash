if [ -z "${DISTRO_NAME:-}" ]; then
    echo "DISTRO_NAME is not set! Can not continue"
    exit 1
fi
export DIB_RELEASE=${DIB_RELEASE:-9}
if [[ $DISTRO_NAME =~ "rhel" ]]; then
    export EFI_BOOT_DIR="EFI/redhat"
else
    export EFI_BOOT_DIR="EFI/$DISTRO_NAME"
fi
export DIB_BLOCK_DEVICE=efi
export DIB_INIT_SYSTEM=systemd