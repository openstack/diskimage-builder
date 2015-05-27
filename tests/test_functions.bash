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
        $DIB_CMD -x $type_arg -o $dest_dir/image -n fake-os

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

function run_element_test() {
    test_element=$1
    element=$2

    dest_dir=$(mktemp -d)

    trap "rm -rf $dest_dir /tmp/dib-test-should-fail" EXIT

    if break="after-error" break_outside_target=1 \
        break_cmd="cp \$TMP_MOUNT_PATH/tmp/dib-test-should-fail /tmp/ || true" \
        ELEMENTS_PATH=$DIB_ELEMENTS:$DIB_ELEMENTS/$element/test-elements \
        $DIB_CMD -t tar -o $dest_dir/image -n $element $test_element; then
        if ! [ -f "$dest_dir/image.tar" ]; then
            echo "Error: Build failed for element: $element, test-element: $test_element."
            echo "No image $dest_dir/image.tar found!"
            exit 1
        else
            if tar -t $dest_dir/image.tar | grep -q /tmp/dib-test-should-fail; then
                echo "Error: Element: $element, test-element $test_element should have failed, but passed."
                exit 1
            else
                echo "PASS: Element $element, test-element: $test_element"
            fi
        fi
    else
        if [ -f "/tmp/dib-test-should-fail" ]; then
            echo "PASS: Element $element, test-element: $test_element"
        else
            echo "Error: Build failed for element: $element, test-element: $test_element."
            exit 1
        fi
    fi

    trap EXIT
    rm -rf $dest_dir /tmp/dib-test-should-fail
}
