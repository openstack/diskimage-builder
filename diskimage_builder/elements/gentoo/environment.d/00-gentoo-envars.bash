export DIB_RELEASE=gentoo
export DISTRO_NAME=gentoo
export EFI_BOOT_DIR="EFI/gentoo"

export GENTOO_PORTAGE_CLEANUP=${GENTOO_PORTAGE_CLEANUP:-'True'}
export GENTOO_PYTHON_TARGETS=${GENTOO_PYTHON_TARGETS:-''}
export GENTOO_OVERLAYS=${GENTOO_OVERLAYS:-''}
export GENTOO_EMERGE_DEFAULT_OPTS=${GENTOO_EMERGE_DEFAULT_OPTS:-"--binpkg-respect-use --rebuilt-binaries=y --usepkg=y --with-bdeps=y --binpkg-changed-deps=y --quiet --jobs=2 --autounmask=n"}

# NOTE(JayF): This defines the base gentoo profile version supported
# in DIB. As gentoo is a rolling release distro, the older profiles
# are unsupported.
export GENTOO_BASE_PROFILE="default/linux/${ARCH}/23.0"
export GENTOO_PROFILE=${GENTOO_PROFILE:-$GENTOO_BASE_PROFILE}

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
# iterate over the array, exporting each 'line'
for (( i=0; i<${#GENTOO_EMERGE_ENV[@]}; i++ )); do
    eval export "${GENTOO_EMERGE_ENV[i]}"
done

if [[ "${GENTOO_PROFILE}" == *"systemd"* ]]; then
    export DIB_INIT_SYSTEM=${DIB_INIT_SYSTEM:-'systemd'}
else
    export DIB_INIT_SYSTEM=${DIB_INIT_SYSTEM:-'openrc'}
fi
