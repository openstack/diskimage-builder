#!/bin/bash

set -eux
set -o pipefail

basedir=$(dirname $0)
requested_element=${1:-}
source $basedir/test_functions.bash

function run_on_element {
    test_element=$1
    # our element name is two dirs up
    local element_name=$(basename $(dirname $(dirname $test_element)))
    local element_type=disk
    if [ -f "$test_element/element-type" ]; then
        element_type=$(cat "$test_element/element-type")
    fi
    run_${element_type}_element_test "$(basename $test_element)" "$element_name"
}

if [ -z $requested_element ]; then
    for test_element in $basedir/../elements/*/test-elements/*; do
        if [ -d "$test_element" ]; then
            run_on_element "$test_element"
        fi
    done
else
    for test_element in $basedir/../elements/$requested_element/test-elements/*; do
        if [ -d "$test_element" ]; then
            run_on_element "$test_element"
        fi
    done
fi
