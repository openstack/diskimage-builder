This is the base element.

Almost all users will want to include this in their disk image build,
as it includes a lot of useful functionality.

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
