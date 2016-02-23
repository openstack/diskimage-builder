#!/bin/bash

set -eu
set -o pipefail

#
# run_output_format_test.sh
#
#  Use docker to test generation of various output formats.
#

BASE_DIR=$(cd $(dirname "$0")/.. && pwd)
export DIB_ELEMENTS=$BASE_DIR/elements
export TEST_ELEMENTS=$BASE_DIR/tests/elements
export DIB_CMD=$BASE_DIR/bin/disk-image-create

function build_test_image() {
    format=${1:-}

    if [ -n "$format" ]; then
        type_arg="-t $format"
    else
        type_arg=
        format="qcow2"
    fi
    dest_dir=$(mktemp -d)
    base_dest=$(basename $dest_dir)

    trap "rm -rf $dest_dir; docker rmi $base_dest/image" EXIT

    ELEMENTS_PATH=$DIB_ELEMENTS:$TEST_ELEMENTS \
        $DIB_CMD -x $type_arg --docker-target=$base_dest/image \
        -o $dest_dir/image -n fake-os

    format=$(echo $format | tr ',' ' ')
    for format in $format; do
        if [ $format != 'docker' ]; then
            img_path="$dest_dir/image.$format"
            if ! [ -f "$img_path" ]; then
                echo "Error: No image with name $img_path found!"
                exit 1
            else
                echo "Found image $img_path."
            fi
        else
            if ! docker images | grep $base_dest/image ; then
                echo "Error: No docker image with name $base_dest/image found!"
                exit 1
            else
                echo "Found docker image $base_dest/image"
            fi
        fi
    done

    trap EXIT
    rm -rf $dest_dir
    if docker images | grep $base_dest/image ; then
        docker rmi $base_dest/image
    fi
}

test_formats="tar raw qcow2 docker aci"
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
