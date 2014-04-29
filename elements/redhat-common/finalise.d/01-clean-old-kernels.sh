#!/bin/bash

set -eu
set -o pipefail

install-packages yum-utils

package-cleanup --oldkernels -y --count=1
