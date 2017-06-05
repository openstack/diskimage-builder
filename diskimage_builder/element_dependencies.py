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


class MissingElementException(Exception):
    pass


class AlreadyProvidedException(Exception):
    pass


class MissingOSException(Exception):
    pass


class InvalidElementDir(Exception):
    pass


class Element(object):
    """An element"""

    def _get_element_set(self, path):
        """Get element set from element-[deps|provides] file

        Arguments:
        :param path: path to element description

        :return: the set of elements in the file, or a blank set if
                 the file is not found.
        """
        try:
            with open(path) as f:
                lines = (line.strip() for line in f)
                # Strip blanks, but do we want to strip comment lines
                # too?  No use case at the moment, and comments might
                # break other things that poke at the element-* files.
                lines = (line for line in lines if line)
                return set(lines)
        except IOError as e:
            if e.errno == errno.ENOENT:
                return set([])
            else:
                raise

    def _make_rdeps(self, all_elements):
        """Make a list of reverse dependencies (who depends on us).

           Only valid after _find_all_elements()

           Arguments:
           :param all_elements: dict as returned by _find_all_elements()

           :return: nothing, but elements will have r_depends var
        """

        # note; deliberatly left out of __init__ so that accidental
        # access without init raises error
        self.r_depends = []
        for name, element in all_elements.items():
            if self.name in element.depends:
                self.r_depends.append(element.name)

    def __init__(self, name, path):
        """A new element

        :param name: The element name
        :param path: Full path to element.  element-deps and
                     element-provides files will be parsed
        """
        self.name = name
        self.path = path

        # read the provides & depends files for this element into a
        # set; if the element has them.
        self.provides = self._get_element_set(
            os.path.join(path, 'element-provides'))
        self.depends = self._get_element_set(
            os.path.join(path, 'element-deps'))

        logger.debug("New element : %s", str(self))

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return self.name

    def __str__(self):
        return '%s p:<%s> d:<%s>' % (self.name,
                                     ','.join(self.provides),
                                     ','.join(self.depends))


def _get_elements_dir():
    if not os.environ.get('ELEMENTS_PATH'):
        raise Exception("$ELEMENTS_PATH must be set.")
    return os.environ['ELEMENTS_PATH']


def _expand_element_dependencies(user_elements, all_elements):
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
            raise MissingElementException("Element '%s' not found" % element)

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

    conflicts = set(user_elements) & provided
    if conflicts:
        logger.error(
            "The following elements are already provided by another element")
        for element in conflicts:
            logger.error("%s : already provided by %s",
                         element, provided_by[element])
        raise AlreadyProvidedException()

    if "operating-system" not in provided:
        raise MissingOSException("Please include an operating system element")

    out = final_elements - provided
    return([all_elements[element] for element in out])


def _find_all_elements(paths=None):
    """Build a dictionary Element() objects

    Walk ELEMENTS_PATH and find all elements.  Make an Element object
    for each element we wish to consider.  Note we process overrides
    such that elements specified earlier in the ELEMENTS_PATH override
    those seen later.

    :param paths: A list of paths to find elements in.  If None will
                  use ELEMENTS_PATH from environment

    :return: a dictionary of all elements
    """

    all_elements = {}

    # note we process the later entries *first*, so that earlier
    # entries will override later ones.  i.e. with
    #  ELEMENTS_PATH=path1:path2:path3
    # we want the elements in "path1" to override "path3"
    if not paths:
        paths = list(reversed(_get_elements_dir().split(':')))
    else:
        paths = list(reversed(paths.split(':')))

    logger.debug("ELEMENTS_PATH is: %s", ":".join(paths))

    for path in paths:
        if not os.path.isdir(path):
            raise InvalidElementDir("ELEMENTS_PATH entry '%s' "
                                    "is not a directory " % path)

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

    # Now we have all the elements, make a call on each element to
    # store it's reverse dependencies
    for name, element in all_elements.items():
        element._make_rdeps(all_elements)

    return all_elements


def _get_elements(elements, paths=None):
    """Return the canonical list of Element objects

    This function returns Element objects.  For exernal calls, use
    get_elements which returns a simple tuple & list.

    :param elements: user specified list of elements
    :param paths: element paths, default to environment

    """
    all_elements = _find_all_elements(paths)
    return _expand_element_dependencies(elements, all_elements)


def get_elements(elements, paths=None):
    """Return the canonical list of elements with their dependencies

    .. note::

       You probably do not want to use this!  Elements that require
       access to the list of all other elements should generally use
       the environment variables exported by disk-image-create below.

    :param elements: user specified elements
    :param paths: Alternative ELEMENTS_PATH; default is to use from env

    :return: A de-duplicated list of tuples [(element, path),
             (element, path) ...] with all elements and their
             dependents, including any transitive dependencies.
    """

    elements = _get_elements(elements, paths)
    return [(element.name, element.path) for element in elements]


def expand_dependencies(user_elements, element_dirs):
    """Deprecated method for expanding element dependencies.

    .. warning::

       DO NOT USE THIS FUNCTION.  For compatibility reasons, this
       function does not provide paths to the returned elements.  This
       means the caller must process override rules if two elements
       with the same name appear in element_dirs

    :param user_elements: iterable enumerating the elements a user requested
    :param element_dirs: The ELEMENTS_PATH to process

    :return: a set containing user_elements and all dependent
             elements including any transitive dependencies.
    """
    logger.warning("expand_dependencies() deprecated, use get_elements")
    elements = _get_elements(user_elements, element_dirs)
    return set([element.name for element in elements])


def _output_env_vars(elements):
    """Output eval-able bash strings for IMAGE_ELEMENT vars

    :param elements: list of Element objects to represent
    """
    # first the "legacy" environment variable that just lists the
    # elements
    print("export IMAGE_ELEMENT='%s'" %
          ' '.join([element.name for element in elements]))

    # Then YAML
    output = {}
    for element in elements:
        output[element.name] = element.path
    print("export IMAGE_ELEMENT_YAML='%s'" % yaml.safe_dump(output))

    # Then bash array.  Unfortunately, bash can't export array
    # variables.  So we take a compromise and produce an exported
    # function that outputs the string to re-create the array.
    # You can then simply do
    #  eval declare -A element_array=$(get_image_element_array)
    # and you have it.
    output = ""
    for element in elements:
        output += '[%s]=%s ' % (element.name, element.path)
    print("function get_image_element_array {\n"
          "  echo \"%s\"\n"
          "};\n"
          "export -f get_image_element_array;" % output)


def main():
    diskimage_builder.logging_config.setup()

    parser = argparse.ArgumentParser()
    parser.add_argument('elements', nargs='+',
                        help='display dependencies of the given elements')
    parser.add_argument('--env', '-e', action='store_true',
                        default=False,
                        help=('Output eval-able bash strings for '
                              'IMAGE_ELEMENT variables'))

    args = parser.parse_args(sys.argv[1:])

    elements = _get_elements(args.elements)

    if args.env:
        _output_env_vars(elements)
    else:
        # deprecated compatibility output; doesn't include paths.
        print(' '.join([element.name for element in elements]))

    return 0

if __name__ == "__main__":
    main()
