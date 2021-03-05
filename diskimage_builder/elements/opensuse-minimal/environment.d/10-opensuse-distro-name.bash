export DISTRO_NAME=opensuse
DIB_RELEASE=${DIB_RELEASE:-15.1}
export DIB_RELEASE=${DIB_RELEASE,,}
export EFI_BOOT_DIR="EFI/opensuse"
export DIB_OPENSUSE_PATTERNS=patterns-openSUSE-base
export DIB_INIT_SYSTEM=systemd
