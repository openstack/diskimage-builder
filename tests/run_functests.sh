#!/bin/bash

set -eux
set -o pipefail

element=${1:-}

if [ -z $element ]; then
    $(dirname $0)/image_output_formats.bash
fi
$(dirname $0)/test_elements.bash $element

echo "Tests passed!"
