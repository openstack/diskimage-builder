#!/bin/bash

set -eux
set -o pipefail

sudo apt-get update || true
sudo apt-get install -y --force-yes \
        apt-transport-https \
        bzip2 \
        debootstrap \
        docker.io \
        dosfstools \
        gdisk \
        inetutils-ping \
        lsb-release \
        kpartx \
        python-lzma \
        qemu-utils \
        rpm \
        uuid-runtime \
        yum-utils || \
    sudo yum -y install --enablerepo=epel \
        bzip2 \
        dpkg \
        debootstrap \
        docker \
        dosfstools \
        gdisk \
        kpartx \
        util-linux \
        qemu-img \
        policycoreutils-python || \
    sudo zypper -n install \
        bzip2 \
        debootstrap \
        docker \
        dosfstools \
        gdisk \
        kpartx \
        util-linux \
        python-pyliblzma \
        yum-utils \
        qemu-tools || \
    sudo emerge \
        app-arch/bzip2 \
        app-emulation/qemu \
        dev-python/pyyaml \
        sys-block/parted \
        sys-apps/gptfdisk \
        sys-fs/multipath-tools \
        sys-fs/dosfstools \
        qemu-img \
        yum-utils
