#!/bin/bash

# Dracut is bash too, and it doesn't play nicely with our usual sets
# dib-lint: disable=setu sete setpipefail dibdebugtrace

check() {
    return 0
}

depends() {
    return 0
}

install() {
    inst /bin/targetcli
    inst "$moddir/targetcli-wrapper" /targetcli-wrapper
    inst "$moddir/iscsi-func" /iscsi-func
    # Install all of Python
    # TODO(bnemec): At some point this will need to be extended to support
    # Python 3, but for the moment we aren't using that anyway.
    inst /usr/bin/python
    local all_of_python=()
    while IFS='' read -r -d '' i; do
        all_of_python+=("$i")
    done < <(find /usr/lib64/python2.7/ /usr/lib/python2.7/ -type f -not -name "*.pyc" -not -name "*.pyo" -print0)
    inst_multiple "${all_of_python[@]}"
}
