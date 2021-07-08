#
# Arch gate
#

if [[ "ppc64 ppc64le ppc64el" =~ "$ARCH" ]]; then
    echo "block-device-efi is not supported on Power; use block-device-gpt or block-device-mbr"
    exit 1
fi

export DIB_BLOCK_DEVICE=efi
