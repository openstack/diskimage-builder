====
base
====
This is the base element.

Almost all users will want to include this in their disk image build,
as it includes a lot of useful functionality.

The `DIB_CLOUD_INIT_ETC_HOSTS` environment variable can be used to
customize cloud-init's management of `/etc/hosts`:

 * If the variable is set to something, write that value as
   cloud-init's manage_etc_hosts.

 * If the variable is set to an empty string, don't create
   manage_etc_hosts setting (cloud-init will use its default value).

 * If the variable is not set, use "localhost" for now. Later, not
   setting the variable will mean using cloud-init's default. (To
   preserve diskimage-builder's current default behavior in the
   future, set the variable to "localhost" explicitly.)

Notes:

 * If you are getting warnings during the build about your locale
   being missing, consider installing/generating the relevant locale.
   This may be as simple as having language-pack-XX installed in the
   pre-install stage

 * This element ensures /tmp/ccache will be available in the chroot
   during the root, extra-data, pre-install, install and post-install
   stages.  /tmp/ccache is unavailable during block-device, finalise
   and cleanup stages as it will have been automatically unmounted
   by then.
