# since f22, dnf is the yum replacement.  Mostly it drops in
# unmodified, so while we transision KISS and use this to choose

if [ $DIB_RELEASE -ge 22 ]; then
    export YUM=dnf
else
    export YUM=yum
fi
