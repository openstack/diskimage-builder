Override the default apt.conf
=============================

For APT based systems, if you require specific options for apt operations,
you can define `DIB_APT_CONF` with your favorite apt.conf to override it,
before running devtest.sh.

The new apt.conf will take effect at build time and run time.

If you want to use this element with tripleo-incubator scripts, set `NODE_DIST`
/ `SEED_DIB_EXTRA_ARGS` / `UNDERCLOUD_DIB_EXTRA_ARGS` /
`OVERCLOUD_CONTROL_DIB_EXTRA_ARGS` / `OVERCLOUD_COMPUTE_DIB_EXTRA_ARGS` to
make it take effect at the appropriate time.

For instance, before running devtest.sh:

    export DIB_APT_CONF=/etc/apt/apt.conf
    export NODE_DIST="ubuntu apt-conf"
