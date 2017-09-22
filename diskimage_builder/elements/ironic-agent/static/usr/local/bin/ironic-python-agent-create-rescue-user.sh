#!/bin/bash

if [ "${DIB_DEBUG_TRACE:-0}" -gt 0 ]; then
    set -x
fi
set -eu
set -o pipefail

echo "Adding rescue user with root privileges..."
crypted_pass=$(</etc/ipa-rescue-config/ipa-rescue-password)
useradd -m rescue -G wheel -p $crypted_pass
echo "rescue ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/rescue
