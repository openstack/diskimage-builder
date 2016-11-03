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


# simply wrap the dib-run-parts in lib
#
# Note to would-be modifiers : the same dib-run-parts script we are
# calling in "lib" here is actually copied into the chroot's
# /usr/local/bin by the dib-run-parts element, where it is run diretly
# by disk-image-create.  Ergo, if you do something clever in here, it
# won't be reflected in the dib-run-parts that actually runs in the
# chroot.  It may not always be like this, but it does reduce reliance
# on Python inside the chroot image.
def main():
    environ = os.environ

    script = "%s/%s" % (diskimage_builder.paths.get_path('lib'),
                        os.path.basename(sys.argv[0]))

    os.execve("/bin/bash", ['bash', script] + sys.argv[1:], environ)
