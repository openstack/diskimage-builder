#!/bin/bash

set -eux
set -o pipefail

basedir=$(dirname $0)
source $basedir/test_functions.bash

for test_element in $basedir/../elements/*/test-elements/*; do
    if [ -d "$test_element" ]; then
        # our element name is two dirs up
        element_name=$(basename $(dirname $(dirname $test_element)))
        element_type=disk
        if [ -f "$test_element/element-type" ]; then
            element_type=$(cat "$test_element/element-type")
        fi
        run_${element_type}_element_test "$(basename $test_element)" "$element_name"
    fi
done
