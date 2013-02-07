Install os-refresh-config.

os-refresh-config uses run-parts to run scripts in a pre-defined set
of directories. Its intended purpose is to quiesce (pre-configure.d),
configure (configure.d), migrate (migration.d), and then activate
(post-configure.d) a configuration on first boot or in response to Heat
Metadata changes.
