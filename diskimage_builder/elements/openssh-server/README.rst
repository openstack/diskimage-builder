==============
openssh-server
==============
This element ensures that openssh server is installed and enabled during boot.

To disable hardening of sshd configuration, you have to set
``DIB_OPENSSH_SERVER_HARDENING`` to 0. This option will configure KexAlgorithms,
Ciphers and MAC following good pratices on
https://infosec.mozilla.org/guidelines/openssh

Note
----
Most cloud images come with the openssh server service installed and enabled
during boot. However, certain cloud images, especially those created by the
\*-minimal elements may not have it installed or enabled. In these cases,
using this element may be helpful to ensure your image will accessible via SSH.
It's usually helpful to combine this element with others such as the
`runtime-ssh-host-keys`.
