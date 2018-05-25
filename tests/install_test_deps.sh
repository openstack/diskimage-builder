#!/bin/bash

set -eux
set -o pipefail

sudo apt-get update || true
sudo apt-get install -y --force-yes \
        docker.io || \
    sudo yum -y install --enablerepo=epel \
         debootstrap \
         dpkg \
         docker || \
    sudo zypper -n install \
        docker || \
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
