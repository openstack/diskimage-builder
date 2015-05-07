#!/bin/bash

set -eux
set -o pipefail

sudo apt-get update || true
sudo apt-get install -y qemu-utils kpartx debootstrap || \
    sudo yum -y install qemu-img kpartx debootstrap
