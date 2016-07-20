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

"""Export paths"""

import os
import pkg_resources
import sys


def get_path(var):
    if var == "lib":
        return os.path.abspath(
            pkg_resources.resource_filename(__name__, "lib"))
    elif var == "elements":
        return os.path.abspath(
            pkg_resources.resource_filename(__name__, "elements"))
    else:
        print("Unknown path request!")
        sys.exit(1)


def show_path(var):
    print(get_path(var))
