#!/bin/bash

set -eux
set -o pipefail

sudo apt-get update || true
sudo apt-get install -y qemu-utils kpartx || \
    sudo yum -y install qemu-img kpartx
