=======
devuser
=======

Creates a user that is useful for development / debugging. The following
environment variables can be useful for configuration:

Environment Variables
---------------------

DIB_DEV_USER_USERNAME
  :Required: No
  :Default: devuser
  :Description: Username for the created user.

DIB_DEV_USER_SHELL
  :Required: No
  :Default: System default (The useradd default is used)
  :Description: Full path for the shell of the user. This is passed to useradd
    using the -s parameter. Note that this does not install the (possibly)
    required shell package.

DIB_DEV_USER_PWDLESS_SUDO
  :Required: No
  :Default: No
  :Description: Enable passwordless sudo for the user.

DIB_DEV_USER_AUTHORIZED_KEYS
  :Required: No
  :Default: $HOME/.ssh/id_{rsa,dsa}.pub
  :Description: Path to a file to copy into this users' .ssh/authorized_keys
    If this is not specified then an attempt is made to use a the building
    user's public key. To disable this behavior specify an invalid path for
    this variable (such as /dev/null).

DIB_DEV_USER_PASSWORD
  :Required: No
  :Default: Password is disabled
  :Description: Set the default password for this user. This is a fairly
    insecure method of setting the password and is not advised.
