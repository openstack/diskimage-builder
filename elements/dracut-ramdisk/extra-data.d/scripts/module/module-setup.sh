#!/bin/bash

# Dracut is bash too, and it doesn't play nicely with our usual sets
# dib-lint: disable=setu sete setpipefail dibdebugtrace

check() {
    return 0
}

depends() {
    return 0
}

install() {
    inst_hook cmdline 80 "$moddir/deploy-cmdline.sh"
    inst_hook pre-mount 50 "$moddir/init.sh"
}
