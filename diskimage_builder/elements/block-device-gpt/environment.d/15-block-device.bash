#
# Arch gate
#

if [[ "arm64 aarch64" =~ $ARCH ]]; then
    echo "block-device-gpt is not supported on AARCH64; use block-device-efi"
    exit 1
fi

export DIB_BLOCK_DEVICE=gpt
