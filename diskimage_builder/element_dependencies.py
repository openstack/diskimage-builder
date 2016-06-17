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
import errno
import logging
import os
import sys
import yaml

import diskimage_builder.logging_config

logger = logging.getLogger(__name__)


class Element(object):
    """An element"""
    def __init__(self, name, path):
        """A new element

        :param name: The element name
        :param path: Full path to element.  element-deps and
                     element-provides files will be parsed
        """
        self.name = name
        self.path = path
        self.provides = set()
        self.depends = set()

        # read the provides & depends files for this element into a
        # set; if the element has them.
        provides = os.path.join(path, 'element-provides')
        depends = os.path.join(path, 'element-deps')
        try:
            with open(provides) as p:
                self.provides = set([line.strip() for line in p])
        except IOError as e:
            if e.errno == errno.ENOENT:
                pass
            else:
                raise
        try:
            with open(depends) as d:
                self.depends = set([line.strip() for line in d])
        except IOError as e:
            if e.errno == errno.ENOENT:
                pass
            else:
                raise

        logger.debug("New element : %s", str(self))

    def __str__(self):
        return '%s p:<%s> d:<%s>' % (self.name,
                                     ','.join(self.provides),
                                     ','.join(self.depends))


def get_elements_dir():
    if not os.environ.get('ELEMENTS_PATH'):
        raise Exception("$ELEMENTS_PATH must be set.")
    return os.environ['ELEMENTS_PATH']


def expand_dependencies(user_elements, all_elements):
    """Expand user requested elements using element-deps files.

    Arguments:
    :param user_elements: iterable enumerating the elements a user requested
    :param all_elements: Element object dictionary from find_all_elements

    :return: a set containing the names of user_elements and all
             dependent elements including any transitive dependencies.
    """
    final_elements = set(user_elements)
    check_queue = collections.deque(user_elements)
    provided = set()
    provided_by = collections.defaultdict(list)

    while check_queue:
        # bug #1303911 - run through the provided elements first to avoid
        # adding unwanted dependencies and looking for virtual elements
        element = check_queue.popleft()
        if element in provided:
            continue
        elif element not in all_elements:
            logger.error("Element '%s' not found", element)
            sys.exit(1)

        element_obj = all_elements[element]

        element_deps = element_obj.depends
        element_provides = element_obj.provides
        # save which elements provide another element for potential
        # error message
        for provide in element_provides:
            provided_by[provide].append(element)
        provided.update(element_provides)
        check_queue.extend(element_deps - (final_elements | provided))
        final_elements.update(element_deps)

    if "operating-system" not in provided:
        logger.error(
            "Please include an operating system element.")
        sys.exit(-1)

    conflicts = set(user_elements) & provided
    if conflicts:
        logger.error(
            "The following elements are already provided by another element")
        for element in conflicts:
            logger.error("%s : already provided by %s" %
                         (element, provided_by[element]))
        sys.exit(-1)

    return final_elements - provided


def find_all_elements(paths=None):
    """Build a dictionary Element() objects

    Walk ELEMENTS_PATH and find all elements.  Make an Element object
    for each element we wish to consider.  Note we process overrides
    such that elements specified earlier in the ELEMENTS_PATH override
    those seen later.

    :param paths: A list of paths to find elements in.  If None will
                  use ELEMENTS_PATH

    :return: a dictionary of all elements

    """

    all_elements = {}

    # note we process the later entries *first*, so that earlier
    # entries will override later ones.  i.e. with
    #  ELEMENTS_PATH=path1:path2:path3
    # we want the elements in "path1" to override "path3"
    if not paths:
        paths = reversed(get_elements_dir().split(':'))
    for path in paths:
        if not os.path.isdir(path):
            logger.error("ELEMENT_PATH entry '%s' is not a directory", path)
            sys.exit(1)

        # In words : make a list of directories in "path".  Since an
        # element is a directory, this is our list of elements.
        elements = [os.path.realpath(os.path.join(path, f))
                    for f in os.listdir(path)
                    if os.path.isdir(os.path.join(path, f))]

        for element in elements:
            # the element name is the last part of the full path in
            # element (these are all directories, we know that from
            # above)
            name = os.path.basename(element)

            new_element = Element(name, element)
            if name in all_elements:
                logger.warning("Element <%s> overrides <%s>",
                               new_element.path, all_elements[name].path)

            all_elements[name] = new_element

    return all_elements


def main():
    diskimage_builder.logging_config.setup()

    parser = argparse.ArgumentParser()
    parser.add_argument('elements', nargs='+',
                        help='display dependencies of the given elements')
    parser.add_argument('--expand-dependencies', '-d', action='store_true',
                        default=False,
                        help=('(DEPRECATED) print expanded dependencies '
                              'of all args'))
    parser.add_argument('--env', '-e', action='store_true',
                        default=False,
                        help=('Output eval-able bash strings for '
                              'IMAGE_ELEMENT variables'))

    args = parser.parse_args(sys.argv[1:])

    all_elements = find_all_elements()

    if args.expand_dependencies:
        logger.warning("expand-dependencies flag is deprecated,  "
                       "and is now on by default.", file=sys.stderr)

    elements = expand_dependencies(args.elements, all_elements)

    if args.env:
        # first the "legacy" environment variable that just lists the
        # elements
        print("export IMAGE_ELEMENT='%s'" % ' '.join(elements))

        # Then YAML
        output = {}
        for element in elements:
            output[element] = all_elements[element].path
        print("export IMAGE_ELEMENT_YAML='%s'" % yaml.safe_dump(output))

        # Then bash array.  Unfortunately, bash can't export array
        # variables.  So we take a compromise and produce an exported
        # function that outputs the string to re-create the array.
        # You can then simply do
        #  eval declare -A element_array=$(get_image_element_array)
        # and you have it.
        output = ""
        for element in elements:
            output += '[%s]=%s ' % (element, all_elements[element].path)
        print("function get_image_element_array {\n"
              "  echo \"%s\"\n"
              "};\n"
              "export -f get_image_element_array;" % output)
    else:
        print(' '.join(elements))

    return 0

if __name__ == "__main__":
    main()
