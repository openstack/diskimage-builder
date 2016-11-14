======
sysctl
======

Add a sysctl-set-value command which can be run from within an element.
Running this command will cause the sysctl value to be set on boot (by
writing the value to /etc/sysctl.d).

Example usage

::
    sysctl-set-value net.ipv4.ip_forward 1
