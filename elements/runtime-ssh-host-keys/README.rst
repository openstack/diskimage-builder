=====================
runtime-ssh-host-keys
=====================
An element to generate SSH host keys on first boot.

Since ssh key generation is not yet common to all operating systems, we need to
create a DIB element to manage this. We force the removal of the SSH host keys,
then add init scripts to generate them on first boot.

This element currently supports Debian and Ubuntu (both systemd and upstart).
