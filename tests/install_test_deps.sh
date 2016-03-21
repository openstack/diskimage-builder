#!/bin/bash

set -eux
set -o pipefail

sudo apt-get update || true
sudo apt-get install -y \
        debootstrap \
        inetutils-ping \
        kpartx \
        qemu-utils \
        uuid-runtime || \
    sudo yum -y install \
        debootstrap \
        kpartx \
        qemu-img
