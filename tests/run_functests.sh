#!/bin/bash

set -eux
set -o pipefail

$(dirname $0)/image_output_formats.bash
$(dirname $0)/test_elements.bash

echo "Tests passed!"
