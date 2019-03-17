# since RHEL8, dnf is the yum replacement.

if [[ ${DIB_RELEASE} == '8' ]]; then
    export YUM=dnf
elif [[ ${DIB_RELEASE} == '7' ]]; then
    export YUM=yum
fi
