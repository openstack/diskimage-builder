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
    CONF_TYPE="rhel-netscripts"
    SCRIPTS_PATH="/etc/sysconfig/network-scripts/"
elif [ -d "/etc/sysconfig/network/" ]; then
    # SUSE network scripts location
    CONF_TYPE="suse-netscripts"
    SCRIPTS_PATH="/etc/sysconfig/network/"
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
    cat /sys/class/net/${1}/carrier || echo 0
}

function get_if_type() {
    cat /sys/class/net/${1}/type
}

function interface_is_vlan() {
    # Check if this is a vlan interface created on top of an Ethernet interface.
    local interface=$1

    # When the vlan interface is created, its mac address is copied from the
    # underlying address and the address assignment type is set to 2
    mac_addr_type=$(cat /sys/class/net/${interface}/addr_assign_type)
    if [ "$mac_addr_type" != "2" ]; then
        return 1
    fi

    # Only check for vlan interfaces named <interface>.<vlan>
    lower_interface="$(echo $interface | cut -f1 -d'.')"
    if [[ ! -z $lower_interface ]]; then
        mac_addr_type=$(cat /sys/class/net/${lower_interface}/addr_assign_type)
        if [ "$mac_addr_type" == "0" ]; then
            return 0 # interface is vlan
        fi
    fi

    return 1
}

function enable_interface() {
    local interface=$1
    local ipv6_init=$2
    local ipv6_AdvManagedFlag=$3
    local ipv6_AdvOtherConfigFlag=$4

    serialize_me
    if [ "$CONF_TYPE" == "eni" ]; then
        printf "auto $interface\niface $interface inet dhcp\n\n" >>$ENI_FILE
        if [ "$ipv6_init" == "True" ]; then
            # Make DUID-UUID Type 4 (RFC 6355)
            echo "default-duid \"\\x00\\x04$(sed 's/.\{2\}/\\x&/g' < /etc/machine-id)\";" >"/var/lib/dhclient/dhclient6--$interface.lease"
            if [ $ipv6_AdvManagedFlag == "Yes" ]; then
                # IPv6 DHCPv6 Stateful address configuration
                printf "iface $interface inet6 dhcp\n\n" >>$ENI_FILE
                echo "DHCPv6 Stateful Configured."
            elif [ $ipv6_AdvOtherConfigFlag == "Yes" ]; then
                # IPv6 DHCPv6 Stateless address configursation
                printf "iface $interface inet6 auto\n\tdhcp 1\n\n" >>$ENI_FILE
                echo "DHCPv6 Stateless Configured."
            else
                # IPv6 Autoconfiguration (SLAAC)
                printf "iface $interface inet6 auto\tdhcp 0\n\n" >>$ENI_FILE
                echo "IPv6 SLAAC Configured"
            fi
        fi
        printf "\n" >>$ENI_FILE
    elif [ "$CONF_TYPE" == "rhel-netscripts" ]; then
        if [ "$(get_if_type $interface)" == "32" ]; then
            printf "DEVICE=\"$interface\"\nBOOTPROTO=\"dhcp\"\nONBOOT=\"yes\"\nTYPE=\"InfiniBand\"\nCONNECTED_MODE=\"no\"\nDEFROUTE=\"yes\"\nPEERDNS=\"yes\"\nPEERROUTES=\"yes\"\nIPV4_FAILURE_FATAL=\"yes\"\nIPV6INIT=\"no\"" >"${SCRIPTS_PATH}ifcfg-$interface"
        else
            if interface_is_vlan $interface; then
                printf "DEVICE=\"$interface\"\nBOOTPROTO=\"dhcp\"\nONBOOT=\"yes\"\nVLAN=\"yes\"\n" >"${SCRIPTS_PATH}ifcfg-$interface"
            else
                printf "DEVICE=\"$interface\"\nBOOTPROTO=\"dhcp\"\nONBOOT=\"yes\"\nTYPE=\"Ethernet\"\n" >"${SCRIPTS_PATH}ifcfg-$interface"
            fi
            if [ "$ipv6_init" == "True" ]; then
                # Make DUID-UUID Type 4 (RFC 6355)
                echo "default-duid \"\\x00\\x04$(sed 's/.\{2\}/\\x&/g' < /etc/machine-id)\";" >"/var/lib/dhclient/dhclient6--$interface.lease"
                printf "IPV6INIT=\"yes\"\n" >>"${SCRIPTS_PATH}ifcfg-$interface"
                if [ $ipv6_AdvManagedFlag == "Yes" ]; then
                    # IPv6 DHCPv6 Stateful address configuration
                    printf "IPV6_FORCE_ACCEPT_RA=\"yes\"\nDHCPV6C=\"yes\"\n" >>"${SCRIPTS_PATH}ifcfg-$interface"
                    echo "DHCPv6 Stateful Configured"
                elif [ $ipv6_AdvOtherConfigFlag == "Yes" ]; then
                    # IPv6 DHCPv6 Stateless address configursation
                    printf "IPV6_AUTOCONF=\"yes\"\nDHCPV6C=\"yes\"\nDHCPV6C_OPTIONS=\"-S\"\n" >>"${SCRIPTS_PATH}ifcfg-$interface"
                    echo "DHCPv6 Stateless Configured"
                else
                    # IPv6 Autoconfiguration (SLAAC)
                    printf "IPV6_AUTOCONF=\"yes\"\n" >>"${SCRIPTS_PATH}ifcfg-$interface"
                    echo "IPv6 SLAAC Configured"
                fi
            fi
    fi
    elif [ "$CONF_TYPE" == "suse-netscripts" ]; then
        printf "BOOTPROTO=\"dhcp\"\nSTARTMODE=\"auto\"" >"${SCRIPTS_PATH}ifcfg-$interface"
    fi
    echo "Configured $1"

}


function config_exists() {
    local interface=$1
    if [[ "$CONF_TYPE" =~ "netscripts" ]]; then
        if [ -f "${SCRIPTS_PATH}ifcfg-$interface" ]; then
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
    elif interface_is_vlan $interface || [ "$mac_addr_type" == "0" ]; then
        local has_link
        local tries=DIB_DHCP_TIMEOUT
        for ((; tries > 0; tries--)); do
            # Need to set the link up on each iteration
            ip link set dev $interface up &>/dev/null
            has_link=$(get_if_link $interface)
            [ "$has_link" == "1" ] && break
            sleep 1
        done
        if [ "$has_link" == "1" ]; then
            local ipv6_init=False
            local ipv6_AdvManagedFlag=No
            local ipv6_AdvOtherConfigFlag=No
            if type rdisc6 &>/dev/null; then
                # We have rdisc6, let's try to configure IPv6 autoconfig/dhcpv6
                tries=DIB_DHCP_TIMEOUT
                for ((; tries > 0; tries--)); do
                    # Need to retry this, link-local-address required for
                    # Neighbor Discovery, DHCPv6 etc.
                    set +e # Do not exit on error, capture rdisc6 error codes.
                    RA=$(rdisc6 --retry 3 --single "$interface" 2>/dev/null)
                    local return_code=$?
                    set -e # Re-enable exit on error.
                    if [ $return_code -eq 0 ]; then
                        ipv6_init=True
                        ipv6_AdvManagedFlag=$(echo "$RA" | grep "Stateful address conf." | awk -F: '{ print $2 }')
                        ipv6_AdvOtherConfigFlag=$(echo "$RA" | grep "Stateful other conf." | awk -F: '{ print $2 }')
                        break
                    elif [ $return_code -eq 1 ]; then
                        sleep 1
                    elif [ $return_code -eq 2 ]; then
                        # If rdisc6 does not receive any response after the
                        # specified number of attempts waiting for wait_ms
                        # (1000ms by default) milliseconds each time, it will
                        # exit with code 2.
                        break
                    fi
                done
            else
                echo "rdisc6 not available, skipping IPv6 configuration."
            fi
            enable_interface "$interface" "$ipv6_init" "$ipv6_AdvManagedFlag" "$ipv6_AdvOtherConfigFlag"
        else
            echo "No link detected, skipping"
        fi
    else
        echo "Device has generated MAC, skipping."
    fi
}

if [ -n "$INTERFACE" ]; then
    inspect_interface $INTERFACE
else
    for iface in $(ls /sys/class/net | grep -v ^lo$); do
        inspect_interface $iface
    done
fi
