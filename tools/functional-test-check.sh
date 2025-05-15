#!/bin/bash -ex

LOGDIR=/home/zuul/zuul-output/logs

# Set to indiciate an error return
RETURN=0
FAILURE_REASON=""

cat > /tmp/ssh_wrapper <<EOF
#!/bin/bash -ex
sudo -H -u zuul ssh -o StrictHostKeyChecking=no -i $HOME/.ssh/id_dib root@\$@

EOF
sudo chmod 0755 /tmp/ssh_wrapper

function sshintonode {
    node=$1

    /tmp/ssh_wrapper $node ls /

    # Check that the root partition grew on boot; it should be a 5GiB
    # partition minus some space for the boot partition.  However
    # emperical evidence suggests there is some modulo maths going on,
    # (possibly with alignment?) that means we can vary up to even
    # 64MiB.  Thus we choose an expected value that gives us enough
    # slop to avoid false matches, but still indicates we resized up.
    root_size=$(/tmp/ssh_wrapper $node -- lsblk -rbno SIZE /dev/vda1)
    expected_root_size=$(( 5000000000 ))
    if [[ $root_size -lt $expected_root_size ]]; then
        echo "*** Root device does not appear to have grown: $root_size"
        FAILURE_REASON="Root partition of $name does not appear to have grown: $root_size < $expected_root_size"
        RETURN=1
    fi

    # Check we saw metadata deployed to the config-drive
    /tmp/ssh_wrapper $node \
        "dd status=none if=/dev/sr0 | tr -cd '[:print:]' | grep -q test-server.novalocal"
    if [[ $? -ne 0 ]]; then
        echo "*** Failed to find metadata in config-drive"
        FAILURE_REASON="Failed to find meta-data in config-drive for $node"
        RETURN=1
    fi

    # Debugging that we're seeing the right node
    /tmp/ssh_wrapper $node -- "cat /etc/os-release; blkid"

    # This ensures DIB setup the bootloader kernel arguments correctly
    # by looking for the default console setup it does.  In the past
    # we have seen issues with bootloader installation for all sorts
    # of reasons (our errors and upstream changes); but generally what
    # has happened is that case grub has silently fallen-back to
    # "guessing" from the running build-system what kernel flags to
    # use.
    #
    # DIB images should be booting from a root device labeled
    # "cloudimg-rootfs".  In the gate, where you're *using* a
    # DIB-image to build a DIB-image, it's /proc/cmdline contains
    # "root=LABEL=cloudimg-rootfs" and a misconfigured grub can
    # actually guess the correct root device.  However, when this
    # builds an image in production on a totally different host you
    # get a non-booting, wrong image.  Ergo, although this is mostly
    # what we're interested in validating, this is not a reliable
    # thing to test directly.
    #
    # So below, we probe for something else; the console setup that
    # DIB will put in.  If this is missing, it's an indication that
    # the bootloader is not setting up the kernel arguments correctly.
    kernel_cmd_line=$(/tmp/ssh_wrapper $node -- cat /proc/cmdline)
    echo "Kernel command line: ${kernel_cmd_line}"
    if [[ ! $kernel_cmd_line =~ 'console=tty0 console=ttyS0,115200' ]]; then
       echo "*** Failed to find correct kernel boot flags"
       FAILURE_REASON="Failed to find correct kernel boot flags $node"
       RETURN=1
    fi

    # Ensure glean services have loaded
    # The output is like:
    # ---
    #  glean-early.service loaded active exited    Early glean execution
    #  glean@ens3.service  loaded active exited    Glean for interface ens3 with NetworkManager
    #  glean@lo.service    loaded active exited    Glean for interface lo with NetworkManager
    # ---
    # So if we see anything other than 'loaded active exited' we have a problem.
    glean_status=$(/tmp/ssh_wrapper $node -- "systemctl | egrep 'glean[@|-]' | { grep -v 'loaded active exited' || true; }")
    if [[ ${glean_status} != '' ]]; then
        echo "*** Glean not loaded correctly"
        echo "*** saw: ${glean_status}"
        FAILURE_REASON="Failed to start glean correctly"
        RETURN=1
    fi
}

function checknm {
    node=$1
    state='ready'
    nm_output=$(/tmp/ssh_wrapper $node -- nmcli c)

    # virtio device is eth0 on older, ens3 on newer
    if [[ ! ${nm_output} =~ (eth0|ens3) ]]; then
        echo "*** Failed to find interface in NetworkManager connections"
        /tmp/ssh_wrapper $node -- nmcli c
        /tmp/ssh_wrapper $node -- nmcli device
        FAILURE_REASON="Failed to find interface in NetworkManager connections"
        RETURN=1
    fi
}

(
# check ssh for root user
sshintonode test-server
# networkmanager check
# TODO(jeblair): This should not run in all cases; in fact, most of
# this checking should move into the dib repo
#checknm test-image
# userdata check
) |& tee "$LOGDIR/functional-checks.log"

set -o errexit

openstack --os-cloud devstack image show test-image
openstack --os-cloud devstack server list
openstack --os-cloud devstack server show test-server

if [[ -n "${FAILURE_REASON}" ]]; then
    echo "${FAILURE_REASON}"
fi
exit $RETURN
