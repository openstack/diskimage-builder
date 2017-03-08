# Copyright 2016 Ian Wienand (iwienand@redhat.com)
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import os.path
import runpy
import sys

import diskimage_builder.paths


# borrowed from pip:locations.py
def running_under_virtualenv():
    """Return True if we're running inside a virtualenv, False otherwise."""
    if hasattr(sys, 'real_prefix'):
        return True
    elif sys.prefix != getattr(sys, "base_prefix", sys.prefix):
        return True
    return False


def activate_venv():
    if running_under_virtualenv():
        activate_this = os.path.join(sys.prefix, "bin", "activate_this.py")
        globs = runpy.run_path(activate_this, globals())
        globals().update(globs)
        del globs


def main():
    # If we are called directly from a venv install
    # (/path/venv/bin/disk-image-create) then nothing has added the
    # virtualenv bin/ dir to $PATH.  the exec'd script below will be
    # unable to find call other dib tools like dib-run-parts.
    #
    # One solution is to say that you should only ever run
    # disk-image-create in a shell that has already sourced
    # bin/activate.sh (all this really does is add /path/venv/bin to
    # $PATH).  That's not a great interface as resulting errors will
    # be very non-obvious.
    #
    # We can detect if we are running in a virtualenv and use
    # virtualenv's "activate_this.py" script to activate it ourselves
    # before we call the script.  This ensures we have the path setting
    activate_venv()

    environ = os.environ

    # pre-seed some paths for the shell script
    environ['_LIB'] = diskimage_builder.paths.get_path('lib')

    # export the path to the current python
    if not os.environ.get('DIB_PYTHON_EXEC'):
        os.environ['DIB_PYTHON_EXEC'] = sys.executable

    # we have to handle being called as "disk-image-create" or
    # "ramdisk-image-create".  ramdisk-iamge-create is just a symlink
    # to disk-image-create
    # XXX: we could simplify things by removing the symlink, and
    # just setting IS_RAMDISK in environ here depending on sys.argv[1]
    script = "%s/%s" % (diskimage_builder.paths.get_path('lib'),
                        os.path.basename(sys.argv[0]))

    os.execve("/bin/bash", ['bash', script] + sys.argv[1:], environ)
