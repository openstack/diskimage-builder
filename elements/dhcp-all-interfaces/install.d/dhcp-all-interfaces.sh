#!/bin/bash

if [ ${DIB_DEBUG_TRACE:-0} -gt 0 ]; then
    set -x
fi
set -eu
set -o pipefail

INTERFACE=${1:-} #optional, if not specified configure all available interfaces
ENI_FILE="/etc/network/interfaces"

PATH=/sbin:$PATH

if [ -d "/etc/network" ]; then
    CONF_TYPE="eni"
elif [ -d "/etc/sysconfig/network-scripts/" ]; then
    CONF_TYPE="netscripts"
else
    echo "Unsupported network configuration type!"
    exit 1
fi

ARGS="$0 $@"

function serialize_me() {
    if [ "$CONF_TYPE" == "eni" ]; then
        # Serialize runs so that we don't miss hot-add interfaces
        FLOCKED=${FLOCKED:-}
        if [ -z "$FLOCKED" ] ; then
            FLOCKED=true exec flock -x $ENI_FILE $ARGS
        fi
    fi
}

function get_if_link() {
    cat /sys/class/net/${1}/carrier
}

function enable_interface() {
    local interface=$1

    serialize_me
    if [ "$CONF_TYPE" == "eni" ]; then
        printf "auto $interface\niface $interface inet dhcp\n\n" >>$ENI_FILE
    elif [ "$CONF_TYPE" == "netscripts" ]; then
        printf "DEVICE=\"$interface\"\nBOOTPROTO=\"dhcp\"\nONBOOT=\"yes\"\nTYPE=\"Ethernet\"" >"/etc/sysconfig/network-scripts/ifcfg-$interface"
    fi
    echo "Configured $1"

}

function config_exists() {
    local interface=$1
    if [ "$CONF_TYPE" == "netscripts" ]; then
        if [ -f "/etc/sysconfig/network-scripts/ifcfg-$interface" ]; then
            return 0
        fi
    else
        if ifquery $interface >/dev/null 2>&1; then
            if [ -z "$(ifquery $interface 2>&1)" ]; then
                return 1
            else
                return 0
            fi
        else
            return 1
        fi
    fi
    return 1
}

function inspect_interface() {
    local interface=$1
    local mac_addr_type
    mac_addr_type=$(cat /sys/class/net/${interface}/addr_assign_type)

    echo -n "Inspecting interface: $interface..."
    if config_exists $interface; then
        echo "Has config, skipping."
    elif [ "$mac_addr_type" != "0" ]; then
        echo "Device has generated MAC, skipping."
    else
        ip link set dev $interface up &>/dev/null

        local has_link
        local tries
        for ((tries = 0; tries < 20; tries++)); do
            has_link=$(get_if_link $interface)
            [ "$has_link" == "1" ] && break
            sleep 1
        done
        if [ "$has_link" == "1" ]; then
            enable_interface "$interface"
        else
            echo "No link detected, skipping"
        fi
    fi
}

if [ -n "$INTERFACE" ]; then
    inspect_interface $INTERFACE
else
    for iface in $(ls /sys/class/net | grep -v ^lo$); do
        inspect_interface $iface
    done
fi
