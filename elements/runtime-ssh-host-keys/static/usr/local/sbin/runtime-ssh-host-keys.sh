#!/bin/bash
# Copyright 2016 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
# dib-lint: disable=dibdebugtrace setpipefail

set -exu

# We are running into race conditions with glean, which ssh-keygen -A is
# not handling properly.  So, create a new script to first check if the
# file exists, then use 'yes' to disable overwriting of existing files.

for key in dsa ecdsa ed25519 rsa; do
    FILE=/etc/ssh/ssh_host_${key}_key
    if ! [ -f $FILE ]; then
        /usr/bin/yes n | /usr/bin/ssh-keygen -f $FILE -N '' -t $key
    fi
done
