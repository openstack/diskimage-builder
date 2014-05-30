SYSTEMD_PC_FILE="/usr/share/pkgconfig/systemd.pc"
SYSTEMD_SYSTEM_UNIT_DIR="/lib"
if [ -f $SYSTEMD_PC_FILE ]; then
    SYSTEMD_SYSTEM_UNIT_DIR=$(awk \
        '/systemdsystemunitdir=/ {split($0,a,"=");print a[2]}' \
        $SYSTEMD_PC_FILE)
fi
export SYSTEMD_SYSTEM_UNIT_DIR
