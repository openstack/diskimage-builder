# Copyright 2012 Hewlett-Packard Development Company, L.P.
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
import sys


class StubPackage(object):
    pass


# load all tests from /elements/*/tests/ dirs.
# conceptually load_tests should be in __init__, but see
# http://bugs.python.org/issue16662 instead. So, its here in test_elements.py
def load_tests(loader, tests, pattern):
    """load tests for diskimage_builder elements."""
    if pattern is None:
        # http://bugs.python.org/issue11218
        pattern = "test*.py"
    this_dir = os.path.dirname(__file__)
    elements_dir = os.path.join(this_dir, "..", "..", "elements")
    # Make a fake elements top level package, as discovery doesn't let us
    # override the python path.
    package = StubPackage()
    package.__path__ = [elements_dir]
    sys.modules['elements'] = package
    elements = os.listdir(elements_dir)
    for element in elements:
        element_dir = os.path.join(elements_dir, element)
        tests_path = os.path.join(element_dir, "tests")
        if (not os.path.isdir(tests_path) or
                not os.path.isfile(os.path.join(tests_path, '__init__.py'))):
            continue
        # Create a 'package' for the element, so it can be imported.
        package = StubPackage()
        package.__path__ = [element_dir]
        sys.modules['elements.%s' % element] = package
        # Try importing the test module
        package_tests = loader.discover(start_dir=tests_path, pattern=pattern)
        tests.addTests(package_tests)
    return tests
