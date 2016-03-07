==========
dib-python
==========

Adds a symlink to /usr/local/bin/dib-python which points at either a python2
or python3 executable. This is useful for creating #! lines for scripts that
are compatible with both python2 and python3.

This does not install a python if one does not exist, and instead fails.
