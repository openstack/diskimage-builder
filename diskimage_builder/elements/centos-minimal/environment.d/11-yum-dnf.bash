if [[ $DIB_RELEASE == "7" ]]; then
    export YUM=yum
else
    export YUM=dnf
fi
