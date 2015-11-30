============
local-config
============
Copies local user settings such as .ssh/authorized\_keys and $http\_proxy into
the image.

Environment Variables
---------------------

DIB_LOCAL_CONFIG_USERNAME
  :Required: No
  :Default: root
  :Description: Username used when installing .ssh/authorized\_keys.
