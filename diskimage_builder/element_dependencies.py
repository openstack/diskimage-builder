# Copyright 2013 Hewlett-Packard Development Company, L.P.
# All Rights Reserved.
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

import argparse
import os
import sys


def get_elements_dir():
    if not os.environ.get('ELEMENTS_PATH'):
        raise Exception("$ELEMENTS_PATH must be set.")
    return os.environ['ELEMENTS_PATH']


def dependencies(element, elements_dir=None):
    """Return the non-transitive list of dependencies for a single element.

    :param user_elements: iterable enumerating elements a user has requested
    :param elements_dir: the elements dir to read from. If not supplied,
                         inferred by calling get_elements_dir().

    :return: a set just containing all elements that the specified element
             depends on.
    """
    if elements_dir is None:
        elements_dir = get_elements_dir()

    for path in elements_dir.split(':'):
        element_deps_path = (os.path.join(path, element, 'element-deps'))
        try:
            with open(element_deps_path) as element_deps:
                return set([line.strip() for line in element_deps])
        except IOError as e:
            if os.path.exists(os.path.join(path, element)) and e.errno == 2:
                return set()
            if e.errno == 2:
                continue
            else:
                raise

    sys.stderr.write("ERROR: Element '%s' not found in '%s'\n" %
                     (element, elements_dir))
    exit(-1)


def expand_dependencies(user_elements, elements_dir=None):
    """Expand user requested elements using element-deps files.

    Arguments:
    :param user_elements: iterable enumerating the elements a user requested
    :param elements_dir: the elements dir to read from. Passed directly to
                         dependencies()

    :return: a set containing user_elements and all dependent elements
             including any transitive dependencies.
    """
    final_elements = set(user_elements)
    check_queue = list(user_elements)

    while check_queue:
        element = check_queue.pop()
        deps = dependencies(element, elements_dir)
        check_queue.extend(deps - final_elements)
        final_elements.update(deps)

    return final_elements


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('elements', nargs='+',
                        help='elements to inspect')
    parser.add_argument('--expand-dependencies', '-d', action='store_true',
                        default=False,
                        help='Print expanded dependencies of all args')

    args = parser.parse_args(argv[1:])

    if args.expand_dependencies:
        print(' '.join(expand_dependencies(args.elements)))
        return 0

    sys.stderr.write("ERROR: please choose an option.\n")
    return -1
