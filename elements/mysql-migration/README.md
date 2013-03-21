Migrate data from another MySQL server into the local one using
os-config-applier and os-refresh-config.

Please note the migration process is *destructive* to any data currently
in the MySQL database running on the target host. Safeguards are in
place to ensure the process only happens once on any machine.

Configuration
-------------

Pass in Heat Metadata with the following structure in the
OpenStack::Config sub-key.

    mysql:
      users:
        root:
          username: rootuser
          password: XXXXXXX
        dump:
          username: dumpuser
          password: XXXXXXX
    mysql-migration:
      bootstrap_host: x.y.z
      slave_user: slave-bot1
      slave_password: XXXXXXXX

The migration process assumes `dump` and `root` exist on the
`bootstrap_host` and have access from this host.

The `dump` user will be used to dump data from `bootstrap_host`. The
`root` user will be used for localhost access after the database is
migrated. If `slave_user` and `slave_password` are set to non-empty
strings, replication will be setup against the `bootstrap_host` using
this user/password combination.

Special /root/.my.cnf
---------------------

As a convenience, we copy the given `dump` and `root` user names and
passwords to /root/.my.cnf after migration. If this file is overwritten,
they will also be available as /root/metadata.my.cnf
