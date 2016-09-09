=============
dynamic-login
=============

This element insert a helper script in the image that allows users to
dynamically configure credentials at boot time. This is specially useful
for troubleshooting.

Troubleshooting an image can be quite hard, specially if you can not get
a prompt you can enter commands to find out what went wrong. By default,
the images (specially ramdisks) doesn't have any SSH key or password for
any user. Of course one could use the ``devuser`` element to generate
an image with SSH keys and user/password in the image but that would be
a massive security hole and very it's discouraged to run in production
with a ramdisk like that.

This element allows the operator to inject a SSH key and/or change the
root password dynamically when the image boots. Two kernel command line
parameters are used to do it:

sshkey
  :Description: If the operator append sshkey="$PUBLIC_SSH_KEY" to the
                kernel command line on boot, the helper script will append
                this key to the root user authorized_keys.

rootpwd
  :Description: If the operator append rootpwd="$ENCRYPTED_PASSWORD" to the
                kernel command line on boot, the helper script will set the
                root password to the one specified by this option. Note that
                this password must be **encrypted**. Encrypted passwords
                can be generated using the ``openssl`` command, e.g:
                *openssl passwd -1*.


.. note::
   The value of these parameters must be **quoted**, e.g: sshkey="ssh-rsa
   BBBA1NBzaC1yc2E ..."


.. warning::
    Some base operational systems might require selinux to be in
    **permissive** or **disabled** mode so that you can log in
    the image. This can be achieved by building the image with the
    ``selinux-permissive`` element for diskimage-builder or by passing
    ``selinux=0`` in the kernel command line. RHEL/CentOS are examples
    of OSs which this is true.
