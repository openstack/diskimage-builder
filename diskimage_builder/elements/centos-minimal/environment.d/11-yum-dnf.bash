if [ $DIB_RELEASE -ge 8 ]; then
    export YUM=dnf
else
    export YUM=yum
fi
