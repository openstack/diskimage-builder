==================
pip-and-virtualenv
==================

This element installs pip and virtualenv in the image. If the package
installtype is used then these programs are installed from distribution
packages. If the source installtype is used these programs are installed
from get-pip.py and pip (respectively).

To install pip and virtualenv from package:

  export DIB_INSTALLTYPE_pip_and_virtualenv=package
