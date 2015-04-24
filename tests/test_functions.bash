export TEST_ELEMENTS=$(dirname $0)/elements
export DIB_ELEMENTS=$(dirname $0)/../elements
export DIB_CMD=$(dirname $0)/../bin/disk-image-create

function build_test_image() {
    format=${1:-}

    if [ -n "$format" ]; then
        type_arg="-t $format"
    else
        type_arg=
        format="qcow2"
    fi
    dest_dir=$(mktemp -d)

    trap "rm -rf $dest_dir" EXIT

    ELEMENTS_PATH=$DIB_ELEMENTS:$TEST_ELEMENTS \
        $DIB_CMD $type_arg -o $dest_dir/image -n fake-os

    format=$(echo $format | tr ',' ' ')
    for format in $format; do
        img_path="$dest_dir/image.$format"
        if ! [ -f "$img_path" ]; then
            echo "Error: No image with name $img_path found!"
            exit 1
        else
            echo "Found image $img_path."
        fi
    done

    trap EXIT
    rm -rf $dest_dir
}
