#!/bin/bash

set -eu
set -o pipefail

BASE_DIR=$(cd $(dirname "$0")/.. && pwd)
export DIB_ELEMENTS=$BASE_DIR/elements
export DIB_CMD=$BASE_DIR/bin/disk-image-create

#
# Default skip tests
#
#  For time reasons, we do not run these tests by default; i.e. these
#  tests are not run by "tox -e func" in the gate.
#
DEFAULT_SKIP_TESTS=(
    # we run version pinned test in gate (this just runs latest)
    fedora/build-succeeds
    # in non-voting
    gentoo/build-succeeds
)

# run_disk_element_test <test_element> <element>
#  Run a disk-image-build .tar build of ELEMENT including any elements
#  specified by TEST_ELEMENT
function run_disk_element_test() {
    local test_element=$1
    local element=$2
    local dest_dir=$(mktemp -d)

    trap "rm -rf $dest_dir /tmp/dib-test-should-fail" EXIT

    if break="after-error" break_outside_target=1 \
        break_cmd="cp \$TMP_MOUNT_PATH/tmp/dib-test-should-fail /tmp/ 2>&1 > /dev/null || true" \
        DIB_SHOW_IMAGE_USAGE=1 \
        ELEMENTS_PATH=$DIB_ELEMENTS:$DIB_ELEMENTS/$element/test-elements \
        $DIB_CMD -x -t tar,qcow2 -o $dest_dir/image -n $element $test_element; then

        if ! [ -f "$dest_dir/image.qcow2" ]; then
            echo "Error: qcow2 build failed for element: $element, test-element: $test_element."
            echo "No image $dest_dir/image.qcow2 found!"
        fi

        # check inside the tar for sentinel files
        if ! [ -f "$dest_dir/image.tar" ]; then
            echo "Error: Build failed for element: $element, test-element: $test_element."
            echo "No image $dest_dir/image.tar found!"
            exit 1
        else
            if tar -tf $dest_dir/image.tar | grep -q /tmp/dib-test-should-fail; then
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

# run_ramdisk_element_test <test_element> <element>
#  Run a disk-image-builder default build of ELEMENT including any
#  elements specified by TEST_ELEMENT
function run_ramdisk_element_test() {
    local test_element=$1
    local element=$2
    local dest_dir=$(mktemp -d)

    if ELEMENTS_PATH=$DIB_ELEMENTS/$element/test-elements \
        $DIB_CMD -x -o $dest_dir/image $element $test_element; then
        # TODO(dtantsur): test also kernel presence once we sort out its naming
        # problem (vmlinuz vs kernel)
        if ! [ -f "$dest_dir/image.initramfs" ]; then
            echo "Error: Build failed for element: $element, test-element: $test_element."
            echo "No image $dest_dir/image.initramfs found!"
            exit 1
        else
            echo "PASS: Element $element, test-element: $test_element"
        fi
    else
        echo "Error: Build failed for element: $element, test-element: $test_element."
        exit 1
    fi
}

#
# run_functests.sh
#  run the functional tests for dib elements
#

# find elements that have functional test elements.  TESTS will be an
# array with each value being "element/test-element"
TESTS=()
for e in $DIB_ELEMENTS/*/test-elements/*; do
    test_element=$(echo $e | awk 'BEGIN {FS="/"}{print $NF}')
    element=$(echo $e | awk 'BEGIN {FS="/"}{print $(NF-2)}')
    TESTS+=("$element/$test_element")
done

while getopts ":hl" opt; do
    case $opt in
        h)
            echo "run_functests.sh [-h] [-l] <test> <test> ..."
            echo "  -h : show this help"
            echo "  -l : list available tests"
            echo "  <test> : functional test to run"
            echo "           Special test 'all' will run all tests"
            exit 0
            ;;
        l)
            echo "The available functional tests are:"
            echo
            for t in ${TESTS[@]}; do
                echo "  $t"
            done
            echo
            exit 0
            ;;
        \?)
            echo "Invalid option: -$OPTARG"
            exit 1
            ;;
    esac
done
shift $((OPTIND-1))

# cull the list of tests to run into TESTS_TO_RUN
TESTS_TO_RUN=()
title=""
if [[ -z "$@" ]]; then
    # remove the skipped tests
    title="Running default tests:"
    for test in "${TESTS[@]}"; do
        if [[ " ${DEFAULT_SKIP_TESTS[@]} " =~ " ${test} " ]]; then
            continue
        else
            TESTS_TO_RUN+=("${test}")
        fi
    done
elif [[ $1 == "all" ]]; then
    title="Running all tests:"
    TESTS_TO_RUN=("${TESTS[@]}")
else
    title="Running specified tests:"
    for test in $@; do
        if [[ ! " ${TESTS[@]} " =~ " ${test} " ]]; then
            echo "${test} : not a known test (see -l)"
            exit 1
        fi
        TESTS_TO_RUN+=("${test}")
    done
fi

# print a little status info
echo "------"
echo ${title}
for test in "${TESTS_TO_RUN[@]}"; do
    echo "  ${test}"
done
echo "------"

for test in "${TESTS_TO_RUN[@]}"; do
    # from above; each array value is element/test_element.  split it
    # back up
    element=${test%/*}
    test_element=${test#*/}

    # tests default to disk-based, but "element-type" can optionally
    # override that
    element_type=disk
    element_type_override=$DIB_ELEMENTS/${element}/test-elements/${test_element}/element-type
    if [ -f ${element_type_override} ]; then
        element_type=$(cat ${element_type_override})
    fi

    echo "Running $test ($element_type)"
    run_${element_type}_element_test $test_element $element
done

echo "Tests passed!"
