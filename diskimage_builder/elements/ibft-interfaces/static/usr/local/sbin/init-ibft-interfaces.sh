#!/bin/bash
# dib-lint: disable=dibdebugtrace

set -eux
set -o pipefail

# iscsistart is a part of the dependencies, but check just in case.
if ! iscsistart -v; then
    echo "iscsistart not found, iBFT devices won't be connected"
    exit 1
fi

if iscsistart -f; then
    if ! iscsistart -N; then
        echo "Could not configure iBFT devices"
        exit 1
    fi
    # Make sure the events for new devices are processed
    udevadm settle
else
    echo "No iBFT devices to configure, exiting"
fi
