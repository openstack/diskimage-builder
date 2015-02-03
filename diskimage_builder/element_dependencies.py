# Copyright 2013 Hewlett-Packard Development Company, L.P.
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

from __future__ import print_function
import argparse
import collections
import os
import sys


def get_elements_dir():
    if not os.environ.get('ELEMENTS_PATH'):
        raise Exception("$ELEMENTS_PATH must be set.")
    return os.environ['ELEMENTS_PATH']


def _get_set(element, fname, elements_dir=None):
    if elements_dir is None:
        elements_dir = get_elements_dir()

    for path in elements_dir.split(':'):
        element_deps_path = (os.path.join(path, element, fname))
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
    sys.exit(-1)


def provides(element, elements_dir=None):
    """Return the set of elements provided by the specified element.

    :param element: name of a single element
    :param elements_dir: the elements dir to read from. If not supplied,
                         inferred by calling get_elements_dir().

    :return: a set just containing all elements that the specified element
             provides.
    """
    return _get_set(element, 'element-provides', elements_dir)


def dependencies(element, elements_dir=None):
    """Return the non-transitive set of dependencies for a single element.

    :param element: name of a single element
    :param elements_dir: the elements dir to read from. If not supplied,
                         inferred by calling get_elements_dir().

    :return: a set just containing all elements that the specified element
             depends on.
    """
    return _get_set(element, 'element-deps', elements_dir)


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
    check_queue = collections.deque(user_elements)
    provided = set()

    while check_queue:
        # bug #1303911 - run through the provided elements first to avoid
        # adding unwanted dependencies and looking for virtual elements
        element = check_queue.popleft()
        if element in provided:
            continue
        deps = dependencies(element, elements_dir)
        provided.update(provides(element, elements_dir))
        check_queue.extend(deps - (final_elements | provided))
        final_elements.update(deps)

    if "operating-system" not in provided:
        sys.stderr.write(
            "ERROR: Please include an operating system element.\n")
        sys.exit(-1)

    conflicts = set(user_elements) & provided
    if conflicts:
        sys.stderr.write("ERROR: Following elements were explicitly required "
                         "but are provided by other included elements: %s\n" %
                         ", ".join(conflicts))
        sys.exit(-1)
    return final_elements - provided


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('elements', nargs='+',
                        help='display dependencies of the given elements')
    parser.add_argument('--expand-dependencies', '-d', action='store_true',
                        default=False,
                        help=('(DEPRECATED) print expanded dependencies '
                              'of all args'))

    args = parser.parse_args(argv[1:])

    if args.expand_dependencies:
        print("WARNING: expand-dependencies flag is deprecated,  "
              "and is now on by default.", file=sys.stderr)

    print(' '.join(expand_dependencies(args.elements)))
    return 0
