export DISTRO_NAME=centos
export DIB_RELEASE=${DIB_RELEASE:-7}

# by default, enable DHCP configuration of eth0 & eth1 in network
# scripts.  See yum-minimal for full details
export DIB_YUM_MINIMAL_CREATE_INTERFACES=${DIB_YUM_MINIMAL_CREATE_INTERFACES:-1}
