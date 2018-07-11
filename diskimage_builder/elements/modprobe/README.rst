========
modprobe
========

Allows to configure specific modprobe options on the image.

It contains the following functionalities:

1. Ability to blacklist specific modules using modprobe.d/blacklist.conf.
   In order to use set DIB_MODPROBE_BLACKLIST to the name of your
   module. To disable multiple modules you can set DIB_MODPROBE_BLACKLIST
   to a list of string separated by spaces.

   Example:

     export DIB_MODPROBE_BLACKLIST="igb"

2. Ability to copy specific files into /etc/modprobe.d directory, so it
   allows to configure settings with freedom. To achieve that, the files
   to be copied needs to be placed inside an specific modprobe.d directory
   of the element.
