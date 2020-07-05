export DISTRO_NAME=centos
export DIB_RELEASE=${DIB_RELEASE:-7}

# by default, enable DHCP configuration of eth0 & eth1 in network
# scripts for centos 7.  See yum-minimal for full details.  CentOS 8
# does not come with network-scripts by default so avoid this there.
if [[ "${DIB_RELEASE}" < "8" ]]; then
    export DIB_YUM_MINIMAL_CREATE_INTERFACES=${DIB_YUM_MINIMAL_CREATE_INTERFACES:-1}
else
    export DIB_YUM_MINIMAL_CREATE_INTERFACES=${DIB_YUM_MINIMAL_CREATE_INTERFACES:-0}
fi
