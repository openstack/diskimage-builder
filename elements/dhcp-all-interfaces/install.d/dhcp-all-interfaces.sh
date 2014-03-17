#!/bin/bash

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

if [ "$CONF_TYPE" == "eni" ]; then
    # Serialize runs so that we don't miss hot-add interfaces
    FLOCKED=${FLOCKED:-}
    if [ -z "$FLOCKED" ] ; then
        FLOCKED=true exec flock -x $ENI_FILE $0
    fi
fi

function get_if_link() {
  cat /sys/class/net/${1}/carrier
}

function enable_interface() {
  local interface=$1

  if [ "$CONF_TYPE" == "eni" ]; then
      printf "auto $interface\niface $interface inet dhcp\n\n" >>$ENI_FILE
  elif [ "$CONF_TYPE" == "netscripts" ]; then
      printf "DEVICE=\"$interface\"\nBOOTPROTO=\"dhcp\"\nONBOOT=\"yes\"\nTYPE=\"Ethernet\"" >"/etc/sysconfig/network-scripts/ifcfg-$interface"
  fi
  echo "Configured $1"

}

function disable_interface() {
  local interface=$1

  if [ "$CONF_TYPE" == "netscripts" ]; then
      local IFCFG_FILE="/etc/sysconfig/network-scripts/ifcfg-$interface"
      if [ -f "$IFCFG_FILE" ]; then
          rm $IFCFG_FILE
      else
          echo "No link detected, skipping"
      fi
  else
      echo "No link detected, skipping"
  fi
}

function config_exists() {
    local interface=$1
    if [ "$CONF_TYPE" == "netscripts" ]; then
        if [ -f "/etc/sysconfig/network-scripts/ifcfg-$interface" ]; then
            return 0
        else
            return 1
        fi
    else
        return ifquery $interface >/dev/null 2>&1
    fi
}

function inspect_interface() {
  local interface=$1
  local mac_addr_type="$(cat /sys/class/net/${interface}/addr_assign_type)"

  echo -n "Inspecting interface: $interface..."
  if config_exists $interface; then
    echo "Has config, skipping."
  elif [ "$mac_addr_type" != "0" ]; then
    echo "Device has generated MAC, skipping."
  else
    ip link set dev $interface up &>/dev/null
    HAS_LINK="$(get_if_link $interface)"

    TRIES=10
    while [ "$HAS_LINK" == "0" -a $TRIES -gt 0 ]; do
      HAS_LINK="$(get_if_link $interface)"
      if [ "$HAS_LINK" == "1" ]; then
        break
      else
        sleep 1
      fi
      TRIES=$(( TRIES - 1 ))
    done
    if [ "$HAS_LINK" == "1" ] ; then
      enable_interface "$interface"
    else
      disable_interface "$interface"
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
