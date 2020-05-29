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
import sys

import diskimage_builder.paths


def main():
    environ = os.environ

    # pre-seed some paths for the shell script
    environ['_LIB'] = diskimage_builder.paths.get_path('lib')

    # export the path to the current python
    if not os.environ.get('DIB_PYTHON_EXEC'):
        os.environ['DIB_PYTHON_EXEC'] = sys.executable

    # we have to handle being called as "disk-image-create" or
    # "ramdisk-image-create".  ramdisk-image-create is just a symlink
    # to disk-image-create
    # XXX: we could simplify things by removing the symlink, and
    # just setting IS_RAMDISK in environ here depending on sys.argv[1]
    script = "%s/%s" % (diskimage_builder.paths.get_path('lib'),
                        os.path.basename(sys.argv[0]))

    os.execve("/bin/bash", ['bash', script] + sys.argv[1:], environ)
