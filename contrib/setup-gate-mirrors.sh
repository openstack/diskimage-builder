#!/bin/bash

set -x

#
# This tool creates repo/sources files that point to the mirrors for
# the host region in the OpenStack CI gate.
#

# This pre-created on CI nodes by slave scripts
source /etc/ci/mirror_info.sh

# Tests should probe for this directory and then use the repos/sources
# files inside it for the gate tests.
BASE_DIR=$WORKSPACE/dib-mirror

mkdir -p $BASE_DIR

## REPOS

# all should start with "dib-mirror-"
# gpg check turned off, because we don't have the keys outside the chroot

# fedora-minimal
FEDORA_MIN_DIR=$BASE_DIR/fedora-minimal/yum.repos.d
mkdir -p $FEDORA_MIN_DIR

cat <<EOF > $FEDORA_MIN_DIR/dib-mirror-fedora.repo
[fedora]
name=Fedora \$releasever - \$basearch
failovermethod=priority
baseurl=$NODEPOOL_FEDORA_MIRROR/releases/\$releasever/Everything/\$basearch/os/
enabled=1
metadata_expire=7d
gpgcheck=0
skip_if_unavailable=False
deltarpm=False
deltarpm_percentage=0
EOF

cat <<EOF > $FEDORA_MIN_DIR/dib-mirror-fedora-updates.repo
[updates]
name=Fedora \$releasever - \$basearch - Updates
failovermethod=priority
baseurl=$NODEPOOL_FEDORA_MIRROR/updates/\$releasever/\$basearch/
enabled=1
gpgcheck=0
metadata_expire=6h
skip_if_unavailable=False
deltarpm=False
deltarpm_percentage=0
EOF

# Centos Minimal
CENTOS_MIN_DIR=$BASE_DIR/centos-minimal/yum.repos.d
mkdir -p $CENTOS_MIN_DIR

cat <<EOF > $CENTOS_MIN_DIR/dib-mirror-base.repo
[base]
name=CentOS-\$releasever - Base
baseurl=$NODEPOOL_CENTOS_MIRROR/\$releasever/os/\$basearch/
gpgcheck=0
EOF

cat <<EOF > $CENTOS_MIN_DIR/dib-mirror-updates.repo
#released updates
[updates]
name=CentOS-\$releasever - Updates
baseurl=$NODEPOOL_CENTOS_MIRROR/\$releasever/updates/\$basearch/
gpgcheck=0
EOF

cat <<EOF > $CENTOS_MIN_DIR/dib-mirror-extras.repo
#additional packages that may be useful
[extras]
name=CentOS-\$releasever - Extras
baseurl=$NODEPOOL_CENTOS_MIRROR/\$releasever/extras/\$basearch/
gpgcheck=0
EOF

## apt sources (todo)
