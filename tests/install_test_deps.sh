#!/bin/bash

set -eux
set -o pipefail

sudo apt-get update || true
sudo apt-get install -y --force-yes \
        apt-transport-https \
        debootstrap \
        docker.io \
        inetutils-ping \
        lsb-release \
        kpartx \
        python-lzma \
        qemu-utils \
        rpm \
        uuid-runtime \
        yum-utils || \
    sudo yum -y install \
        debootstrap \
        docker \
        kpartx \
        qemu-img || \
    sudo emerge \
        app-emulation/qemu \
        dev-python/pyyaml \
        sys-block/parted \
        sys-fs/multipath-tools \
        qemu-img \
        yum-utils
