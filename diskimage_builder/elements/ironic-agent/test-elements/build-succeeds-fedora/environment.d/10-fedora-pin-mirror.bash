# Set DIB_DISTRIBUTION_MIRROR if running in openstack gate
if [ -f /etc/ci/mirror_info.sh ]; then
    source /etc/ci/mirror_info.sh
    export DIB_DISTRIBUTION_MIRROR=$NODEPOOL_FEDORA_MIRROR
else
    export DIB_DISTRIBUTION_MIRROR=http://dl.fedoraproject.org/pub/fedora/linux
fi
