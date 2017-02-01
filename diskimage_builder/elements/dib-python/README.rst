==========
dib-python
==========

Adds a symlink to /usr/local/bin/dib-python which points at either a python2
or python3 executable. This is useful for creating #! lines for scripts that
are compatible with both python2 and python3.

This does not install a python if one does not exist, and instead fails.

This also exports a variable DIB_PYTHON_VERSION which will either be '2' or
'3' depending on the python version which dib-python points to.
