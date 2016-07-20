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

# Python Logging Configuration for DIB
# Usage:
# In the main (application) file, do an
#   import logging_config
#   ...
#   logging_config.setup()
# It is then possible to use the normal python logging interface, like
#   logger = logging.getLogger(__name__)
#   logger.info("Info Message")

import os
import os.path
import sys

import diskimage_builder.paths


def main():
    environ = os.environ

    # pre-seed some paths for the shell script
    environ['_LIB'] = diskimage_builder.paths.get_path('lib')

    # we have to handle being called as "disk-image-create" or
    # "ramdisk-image-create".  ramdisk-iamge-create is just a symlink
    # to disk-image-create
    # XXX: we could simplify things by removing the symlink, and
    # just setting IS_RAMDISK in environ here depending on sys.argv[1]
    script = "%s/%s" % (diskimage_builder.paths.get_path('lib'),
                        os.path.basename(sys.argv[0]))

    os.execve("/bin/bash", ['bash', script] + sys.argv[1:], environ)
