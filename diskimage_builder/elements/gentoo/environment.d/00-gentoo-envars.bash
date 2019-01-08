export DIB_RELEASE=gentoo
export DISTRO_NAME=gentoo
export GENTOO_PROFILE=${GENTOO_PROFILE:-'default/linux/amd64/17.0'}
export GENTOO_PORTAGE_CLEANUP=${GENTOO_PORTAGE_CLEANUP:-'True'}
export GENTOO_PYTHON_TARGETS=${GENTOO_PYTHON_TARGETS:-'python2_7 python3_6'}
export GENTOO_PYTHON_ACTIVE_VERSION=${GENTOO_PYTHON_ACTIVE_VERSION:-'python3.6'}
export GENTOO_OVERLAYS=${GENTOO_OVERLAYS:-''}
export GENTOO_EMERGE_DEFAULT_OPTS=${GENTOO_EMERGE_DEFAULT_OPTS:-"--binpkg-respect-use --rebuilt-binaries=y --usepkg=y --with-bdeps=y --binpkg-changed-deps=y --quiet --jobs=2"}

# set the default bash array if GENTOO_EMERGE_ENV is not defined as an array
if ! declare -p GENTOO_EMERGE_ENV  2> /dev/null | grep -q '^declare \-a'; then
    export GENTOO_EMERGE_ENV=('USE="-build"' 'FEATURES="binpkg-multi-instance buildpkg parallel-fetch parallel-install"')
fi
# itterate over the array, exporting each 'line'
for (( i=0; i<${#GENTOO_EMERGE_ENV[@]}; i++ )); do
    eval export "${GENTOO_EMERGE_ENV[i]}"
done
