# Put ccache in path for known compilers
if ! [[ "$PATH" =~ "/usr/lib/ccache" ]] ; then
    export PATH=/usr/lib/ccache:$PATH
fi
export CCACHE_DIR=/tmp/ccache
