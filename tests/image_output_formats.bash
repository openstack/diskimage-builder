#!/bin/bash

set -eux
set -o pipefail

source $(dirname $0)/test_functions.bash

test_formats="tar raw qcow2 docker"
for binary in qemu-img docker ; do
    if [ -z "$(which $binary)" ]; then
        echo "Warning: No $binary binary found, cowardly refusing to run tests."
        exit 0
    fi
done

for format in '' $test_formats; do
    build_test_image $format
    echo "Test passed for output formats '$format'."
done

combined_format=$(echo $test_formats | tr ' ' ',')
build_test_image $combined_format
echo "Test passed for output format '$combined_format'."
