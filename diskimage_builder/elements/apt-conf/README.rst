========
apt-conf
========

This element overrides the default apt.conf for APT based systems.

Environment Variables
---------------------

DIB_APT_CONF:
   :Required: No
   :Default: None
   :Description: To override `DIB_APT_CONF`, set it to the path to your
                 apt.conf. The new apt.conf will take effect at build time and
                 run time.
   :Example: ``DIB_APT_CONF=/etc/apt/apt.conf``
