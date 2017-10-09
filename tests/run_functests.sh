#!/bin/bash

set -eu
set -o pipefail

BASE_DIR=$(cd $(dirname "$0")/.. && pwd)

# then execute tests for elements
export DIB_CMD=disk-image-create
export DIB_ELEMENTS=$(python -c '
import diskimage_builder.paths
diskimage_builder.paths.show_path("elements")')

# Setup sane locale defaults, because this information is leaked into DIB.
export LANG=en_US.utf8
export LC_ALL=

#
# Default skip tests
#
#  For time reasons, we do not run these tests by default; i.e. these
#  tests are not run by "tox -e func" in the gate.
#
DEFAULT_SKIP_TESTS=(
    ##  These are part of the "extras-nv" job
    # These require "zypper" on the host which is not available on
    # all platforms
    opensuse-minimal/build-succeeds
    opensuse-minimal/opensuse423-build-succeeds
    # non-voting; not used by infra currently
    gentoo/build-succeeds
    # Needs infra mirroring to move to voting job
    debian-minimal/stable-build-succeeds
    debian-minimal/stable-vm
    ##

    # These download base images which has shown to be very unreliable
    # in the gate.  Keep them in a -nv job until we can figure out
    # better caching for the images
    opensuse/build-succeeds
    opensuse/opensuse423-build-succeeds
    centos7/build-succeeds
    debian/build-succeeds
    fedora/build-succeeds
    ubuntu/trusty-build-succeeds
    ubuntu/xenial-build-succeeds

    # No longer reasonable to test upstream (lacks a mirror in infra)
    # Note this is centos6 and should probably be removed
    centos/build-succeeds

    # This job is a bit unreliable, even if we get mirroring
    debian-minimal/testing-build-succeeds
)

# The default output formats (specified to disk-image-create's "-t"
# command.  Elements can override with a test-output-formats file
DEFAULT_OUTPUT_FORMATS="tar"

function log_with_prefix {
    local pr=$1
    local log

    while read a; do
        log="[$pr] $a"
        # note: dib logs have timestamp by default now
        echo "${log}"
    done
}

# Log job control messages
function log_jc {
    local msg="$1"
    local log="[JOB-CONTROL] ${msg}"

    if [[ ${LOG_DATESTAMP} -ne 0 ]]; then
        log="$(date +"%Y%m%d-%H%M%S.%N") ${log}"
    fi
    echo "${log}"
}

function job_cnt {
    running_jobs=$(jobs -p)
    echo ${running_jobs} | wc -w
}

# This is needed, because the better 'wait -n' is
# available since bash 4.3 only.
function wait_minus_n {
    if [ "${BASH_VERSINFO[0]}" -gt 4 \
                               -o "${BASH_VERSINFO[0]}" = 4 \
                               -a "${BASH_VERSINFO[1]}" -ge 3 ]; then
        # Good way: wait on any job
        wait -n
        return $?
    else
        # Not that good way: wait on one specific job
        # (others may be finished in the mean time)
        local wait_for_pid=$(jobs -p | head -1)
        wait ${wait_for_pid}
        return $?
    fi
}

# run_disk_element_test <test_element> <element> <use_tmp> <output_formats>
#  Run a disk-image-build build of ELEMENT including any elements
#  specified by TEST_ELEMENT.  Pass OUTPUT_FORMAT to "-t"
function run_disk_element_test() {
    local test_element=$1
    local element=$2
    local dont_use_tmp=$3
    local output_format="$4"

    local use_tmp_flag=""
    local dest_dir=$(mktemp -d)

    if [[ ${KEEP_OUTPUT} -ne 1 ]]; then
        trap "rm -rf $dest_dir" EXIT
    fi

    if [ "${dont_use_tmp}" = "yes" ]; then
        use_tmp_flag="--no-tmpfs"
    fi

    if break="after-error" break_outside_target=1 \
        break_cmd="cp -v \$TMP_MOUNT_PATH/tmp/dib-test-should-fail ${dest_dir} || true" \
        DIB_SHOW_IMAGE_USAGE=1 \
        ELEMENTS_PATH=$DIB_ELEMENTS/$element/test-elements \
        $DIB_CMD -x -t ${output_format} \
                       ${use_tmp_flag} \
                       -o $dest_dir/image -n $element $test_element 2>&1 \
           | log_with_prefix "${element}/${test_element}"; then

        if [[ "qcow2" =~ "$output_format" ]]; then
            if ! [ -f "$dest_dir/image.qcow2" ]; then
                echo "Error: qcow2 build failed for element: $element, test-element: $test_element."
                echo "No image $dest_dir/image.qcow2 found!"
                exit 1
            fi
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
        if [ -f "${dest_dir}/dib-test-should-fail" ]; then
            echo "PASS: Element $element, test-element: $test_element"
        else
            echo "Error: Build failed for element: $element, test-element: $test_element."
            exit 1
        fi
    fi

    rm -f /tmp/dib-test-should-fail

    if [[ ${KEEP_OUTPUT} -ne 1 ]]; then
        # reset trap and cleanup
        trap EXIT
        rm -rf $dest_dir
    fi
}

# run_ramdisk_element_test <test_element> <element>
#  Run a disk-image-builder default build of ELEMENT including any
#  elements specified by TEST_ELEMENT
function run_ramdisk_element_test() {
    local test_element=$1
    local element=$2
    local dest_dir=$(mktemp -d)

    if ELEMENTS_PATH=$DIB_ELEMENTS/$element/test-elements \
        $DIB_CMD -x -o $dest_dir/image $element $test_element \
            | log_with_prefix "${element}/${test_element}"; then
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

#
# Default values
#
JOB_MAX_CNT=1
LOG_DATESTAMP=0
KEEP_OUTPUT=0

#
# Parse args
#
while getopts ":hlj:t" opt; do
    case $opt in
        h)
            echo "run_functests.sh [-h] [-l] <test> <test> ..."
            echo "  -h : show this help"
            echo "  -l : list available tests"
            echo "  -j : parallel job count (default to 1)"
            echo "  -t : prefix log messages with timestamp"
            echo "  -k : keep output directories"
            echo "  <test> : functional test to run"
            echo "           Special test 'all' will run all tests"
            exit 0
            ;;
        l)
            echo "The available functional tests are:"
            echo
            for t in ${TESTS[@]}; do
                echo -n "  $t"
                if [[ " ${DEFAULT_SKIP_TESTS[@]} " =~ " ${t} " ]]; then
                    echo " [skip]"
                else
                    echo " [run]"
                fi
            done
            echo
            exit 0
            ;;
        j)
            JOB_MAX_CNT=${OPTARG}
            echo "Running parallel - using [${JOB_MAX_CNT}] jobs"
            ;;
        t)
            LOG_DATESTAMP=1
            ;;
        k)
            KEEP_OUTPUT=1
            ;;
        \?)
            echo "Invalid option: -$OPTARG"
            exit 1
            ;;
    esac
done
shift $((OPTIND-1))

DONT_USE_TMP="no"
if [ "${JOB_MAX_CNT}" -gt 1 ]; then
    # switch off using tmp dir for image building
    # (The mem check using the tmp dir is currently done
    #  based on the available memory - and not on the free.
    #  See #1618124 for more details)
    DONT_USE_TMP="yes"
fi

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

function wait_and_exit_on_failure {
    local pid=$1

    wait ${pid}
    result=$?

    if [ "${result}" -ne 0 ]; then
        exit ${result}
    fi
    return 0
}

EXIT_CODE=0
for test in "${TESTS_TO_RUN[@]}"; do
    running_jobs_cnt=$(job_cnt)
    log_jc "Number of running jobs [${running_jobs_cnt}] max jobs [${JOB_MAX_CNT}]"
    if [ "${running_jobs_cnt}" -ge "${JOB_MAX_CNT}" ]; then
        log_jc "Waiting for job to finish"
        wait_minus_n
        result=$?

        if [ "${result}" -ne 0 ]; then
            EXIT_CODE=1
            # If a job fails, do not start any new ones.
            break
        fi
    fi

    log_jc "Starting new job"

    # from above; each array value is element/test_element.  split it
    # back up
    element=${test%/*}
    test_element=${test#*/}

    element_dir=$DIB_ELEMENTS/${element}/test-elements/${test_element}/

    # tests default to disk-based, but "element-type" can optionally
    # override that
    element_type=disk
    element_type_override=${element_dir}/element-type
    if [ -f ${element_type_override} ]; then
        element_type=$(cat ${element_type_override})
    fi

    # override the output format if specified
    element_output=${DEFAULT_OUTPUT_FORMATS}
    element_output_override=${element_dir}/test-output-formats
    if [ -f $element_output_override ]; then
        element_output=$(cat ${element_output_override})
    fi

    echo "Running $test ($element_type)"
    run_${element_type}_element_test $test_element $element ${DONT_USE_TMP} "${element_output}" &
done

# Wait for the rest of the jobs
while true; do
    running_jobs_cnt=$(job_cnt)
    log_jc "Number of running jobs left [${running_jobs_cnt}]"

    if [ "${running_jobs_cnt}" -eq 0 ]; then
        break;
    fi

    wait_minus_n
    result=$?

    if [ "${result}" -ne 0 ]; then
        EXIT_CODE=1
    fi
done

if [ "${EXIT_CODE}" -eq 0 ]; then
    echo "Tests passed!"
    exit 0
else
    echo "At least one test failed"
    exit 1
fi
