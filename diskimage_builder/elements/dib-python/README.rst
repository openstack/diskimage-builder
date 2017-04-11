==========
dib-python
==========

Adds a symlink to `/usr/local/bin/dib-python` which points at either a
`python2` or `python3` executable as appropriate.

In-chroot scripts should use this as their interpreter
(`#!/usr/local/bin/dib-python`) to make scripts that are compatible
with both `python2` and `python3`.  We can not assume
`/usr/bin/python` exists, as some platforms have started shipping with
only Python 3.

`DIB_PYTHON` will be exported as the python interpreter.  You should
use this instead of `python script.py` (e.g. `${DIB_PYTHON}
script.py`).  Note you can also call `/usr/local/bin/dib-python
script.py` but in some circumstances, such as creating a `virtualenv`,
it can create somewhat confusing references to `dib-python` that
remain in the built image.

This does not install a python if one does not exist, and instead fails.

This also exports a variable `DIB_PYTHON_VERSION` which will either be
'2' or '3' depending on the python version which dib-python points to.
