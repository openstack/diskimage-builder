==================
journal-to-console
==================

Configure systemd's journal to send all logs to console.  Useful for
debugging issues before you can log into a host, such as network or
authentication issues.

The console can be retrieved from an OpenStack cloud with a command
such as ``openstack console log show <server>``.
