# Put ccache in path for known compilers
for CCACHEDIR in "/usr/lib/ccache" "/usr/lib64/ccache" ; do
    if ! [[ "$PATH" =~ "$CCACHEDIR" ]] ; then
        export PATH=$CCACHEDIR:$PATH
    fi
done
export CCACHE_DIR=/tmp/ccache
