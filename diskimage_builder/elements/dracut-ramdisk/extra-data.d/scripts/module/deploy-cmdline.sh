#!/bin/bash

# NOTE(bnemec): Dracut doesn't like it if we enable these
# dib-lint: disable=setu sete setpipefail dibdebugtrace

# We never let Dracut boot off the specified root anyway, so all
# we need is a value it will accept.
root=/dev/zero
rootok=1

# Dracut doesn't correctly parse the ip argument passed to us.
# Override /proc/cmdline to rewrite it in a way dracut can grok.
sed 's/\(ip=\S\+\)/\1:::off/' /proc/cmdline > /run/cmdline
mount -n --bind -o ro /run/cmdline /proc/cmdline
# Force Dracut to re-read the cmdline args
CMDLINE=
