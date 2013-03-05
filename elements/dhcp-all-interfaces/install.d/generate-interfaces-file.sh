#!/bin/bash

# Generate $INTERFACES_FILE on first boot
# This will add any unconfigured network interfaces to /etc/network/interfaces
#  and configure them for DHCP

INTERFACES_FILE="/etc/network/interfaces"

function get_if_link() {
  cat /sys/class/net/${1}/carrier
}

for interface in $(ls /sys/class/net | grep -v ^lo$) ; do
  echo -n "Inspecting interface: $interface..."
  HAS_CONFIG=$(ifquery $interface >/dev/null 2>&1)
  if [ "$HAS_CONFIG" == "" ]; then
    ip link set dev $interface up >/dev/null 2>&1
    HAS_LINK="$(get_if_link $interface)"

    TRIES=3
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
      printf "auto $interface\r\niface $interface inet dhcp\r\n\r\n" >>$INTERFACES_FILE]
      echo "Configured"
    else
      echo "No link detected, skipping"
    fi
  fi
done
