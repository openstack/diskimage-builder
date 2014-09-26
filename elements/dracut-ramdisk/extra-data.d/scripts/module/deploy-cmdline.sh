#!/bin/bash

# NOTE(bnemec): Dracut doesn't like it if we enable these
# dib-lint: disable=setu sete setpipefail

source /init-func

find_target() {
    local DISK=$(getarg disk)
    local target_disk=
    t=0
    while ! target_disk=$(find_disk "$DISK"); do
        if [ $t -eq 10 ]; then
            break
        fi
        t=$(($t + 1))
        sleep 1
    done
    echo $target_disk
}
root=$(find_target)

if [ -n "$root" ]; then
    rootok=1
fi

# Dracut doesn't correctly parse the ip argument passed to us.
# Override /proc/cmdline to rewrite it in a way dracut can grok.
sed 's/\(ip=\S\+\)/\1:::off/' /proc/cmdline > /run/cmdline
# Map the existing "troubleshoot" kernel param to the Dracut equivalent.
sed -i 's/troubleshoot=/rd.shell=/' /run/cmdline
mount -n --bind -o ro /run/cmdline /proc/cmdline
# Force Dracut to re-read the cmdline args
CMDLINE=
