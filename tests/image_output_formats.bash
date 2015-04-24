#!/bin/bash

set -eux
set -o pipefail

source $(dirname $0)/test_functions.bash

test_formats="tar raw qcow2"
if [ -z "$(which qemu-img)" ]; then
    echo "Warning: No qemu-img binary found, cowardly refusing to run tests."
    exit 0
fi

for format in '' $test_formats; do
    build_test_image $format
    echo "Test passed for output formats '$format'."
done

combined_format=$(echo $test_formats | tr ' ' ',')
build_test_image $combined_format
echo "Test passed for output format '$combined_format'."
