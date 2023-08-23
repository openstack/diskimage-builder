========
fail2ban
========

This element installs the fail2ban binary from the upstream repositories.
In the case of rocky linux, fail2ban lives in epel so the 'epel' element must also be included.

In addition, a compulsory jail.local is expected, localy on the build system, to be inserted in the final image.

Environment Variables
---------------------

DIB_FAIL2BAN_CONF:
   :Required: Yes
   :Default: None
   :Description: The location of a fail2ban.conf file on the Builder system which will be injected into the image
   :Example: ``DIB_FAIL2BAN_CONF=~/home/jail.local``

.. element_deps::
