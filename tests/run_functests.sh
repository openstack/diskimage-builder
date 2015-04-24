#!/bin/bash

set -eux
set -o pipefail

$(dirname $0)/image_output_formats.bash

echo "Tests passed!"
