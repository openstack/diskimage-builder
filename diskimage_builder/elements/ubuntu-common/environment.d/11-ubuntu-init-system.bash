if [[ ${DIB_RELEASE} == "trusty" ]]; then
    export DIB_INIT_SYSTEM=upstart
else
    export DIB_INIT_SYSTEM=systemd
fi
