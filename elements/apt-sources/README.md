# Override the default sources.list

For APT based systems, if your network connection is slow for the default
sources.list in the upstream cloud image, you can define `DIB_APT_SOURCES` with
your favorite sources.list to override it, before running devtest.sh.

The new sources.list will take effect at build time and run time.

If you want to use this element with tripleo-incubator scripts, set `NODE_DIST`
/ `SEED_DIB_EXTRA_ARGS` / `UNDERCLOUD_DIB_EXTRA_ARGS` /
`OVERCLOUD_CONTROL_DIB_EXTRA_ARGS` / `OVERCLOUD_COMPUTE_DIB_EXTRA_ARGS` to make
it take effect at the appropriate time.

For instance, before running devtest.sh:
    export `DIB_APT_SOURCES`=/etc/apt/sources.list
    export `NODE_DIST`="ubuntu apt-sources"
