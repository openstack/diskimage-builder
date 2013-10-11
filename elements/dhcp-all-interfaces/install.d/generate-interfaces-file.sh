#!/bin/bash

# Generate $INTERFACES_FILE on first boot
# This will add any unconfigured network interfaces to /etc/network/interfaces
#  and configure them for DHCP

INTERFACES_FILE="/etc/network/interfaces"

# Serialize runs so that we don't miss hot-add interfaces
FLOCK=${1:-}
if [ -z "$FLOCK" ] ; then
    exec flock -x $INTERFACES_FILE $0 flocked
fi

function get_if_link() {
  cat /sys/class/net/${1}/carrier
}

for interface in $(ls /sys/class/net | grep -v ^lo$) ; do
  echo -n "Inspecting interface: $interface..."
  if ifquery $interface >/dev/null 2>&1 ; then
    echo "Has config, skipping."
  else
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
      printf "auto $interface\niface $interface inet dhcp\n\n" >>$INTERFACES_FILE
      echo "Configured"
    else
      echo "No link detected, skipping"
    fi
  fi
done
