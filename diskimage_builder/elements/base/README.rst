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

The 'DIB_AVOID_PACKAGES_UPDATE' environment variable can be used to
avoid updating all packages, useful when wanting to avoid release
update.

 * 'DIB_AVOID_PACKAGES_UPDATE' default is '0', all packages will be updated.

 * set 'DIB_AVOID_PACKAGES_UPDATE' to '1' to avoid updating all packages.

Notes:

 * If you are getting warnings during the build about your locale
   being missing, consider installing/generating the relevant locale.
   This may be as simple as having language-pack-XX installed in the
   pre-install stage
