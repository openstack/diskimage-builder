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
        qemu-utils \
        uuid-runtime || \
    sudo yum -y install \
        debootstrap \
        docker \
        kpartx \
        qemu-img
