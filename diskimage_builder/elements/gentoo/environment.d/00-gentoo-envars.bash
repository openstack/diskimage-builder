export DIB_RELEASE=gentoo
export DISTRO_NAME=gentoo
export GENTOO_PROFILE=${GENTOO_PROFILE:-'default/linux/amd64/17.1'}
export GENTOO_PORTAGE_CLEANUP=${GENTOO_PORTAGE_CLEANUP:-'True'}
export GENTOO_PYTHON_TARGETS=${GENTOO_PYTHON_TARGETS:-'python2_7 python3_6'}
export GENTOO_PYTHON_ACTIVE_VERSION=${GENTOO_PYTHON_ACTIVE_VERSION:-'python3.6'}
export GENTOO_OVERLAYS=${GENTOO_OVERLAYS:-''}
export GENTOO_EMERGE_DEFAULT_OPTS=${GENTOO_EMERGE_DEFAULT_OPTS:-"--binpkg-respect-use --rebuilt-binaries=y --usepkg=y --with-bdeps=y --binpkg-changed-deps=y --quiet --jobs=2 --autounmask=n"}

# set the default bash array if GENTOO_EMERGE_ENV is not defined as an array
if ! declare -p GENTOO_EMERGE_ENV  2> /dev/null | grep -q '^declare \-a'; then
    declare -a GENTOO_EMERGE_ENV
    GENTOO_EMERGE_ENV+=("USE=\"-build\"")
    GENTOO_EMERGE_ENV+=("FEATURES=\"binpkg-multi-instance buildpkg parallel-fetch parallel-install\"")
    GENTOO_EMERGE_ENV+=("PKGDIR=\"/tmp/portage-pkgdir\"")
    GENTOO_EMERGE_ENV+=("DISTDIR=\"/tmp/portage-distdir\"")
    GENTOO_EMERGE_ENV+=("PORTDIR=\"/tmp/portage-portdir\"")
    export GENTOO_EMERGE_ENV
fi
# itterate over the array, exporting each 'line'
for (( i=0; i<${#GENTOO_EMERGE_ENV[@]}; i++ )); do
    eval export "${GENTOO_EMERGE_ENV[i]}"
done

if [[ "${GENTOO_PROFILE}" == *"systemd"* ]]; then
    export DIB_INIT_SYSTEM=${DIB_INIT_SYSTEM:-'systemd'}
else
    export DIB_INIT_SYSTEM=${DIB_INIT_SYSTEM:-'openrc'}
fi
