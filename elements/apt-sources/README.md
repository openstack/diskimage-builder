Override the default sources.list

For Ubuntu OS, if your network connection is slow for the default sources.list,
you can define DIB_APT_SOURCES with your favorite sources.list to override it,
before running devtest.sh.

The new sources.list will take effect at build time and run time.

If you want to use this element in tripleo project, set NODE_DIST or
EXTRA_ELEMENTS / UNDERCLOUD_DIB_EXTRA_ARGS / OVERCLOUD_DIB_EXTRA_ARGS
to make it take effect at build time and run time.

e.g. before running devtest.sh:
export DIB_APT_SOURCES=/etc/apt/sources.list
export NODE_DIST="ubuntu apt-sources"
