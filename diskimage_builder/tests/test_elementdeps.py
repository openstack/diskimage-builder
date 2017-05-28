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

import logging
import os

import fixtures
import testtools

from diskimage_builder import element_dependencies

logger = logging.getLogger(__name__)

data_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'test-elements'))


def _populate_element(element_dir, element_name, element_deps=[], provides=[]):
    logger.debug("Populate %s <%s>", element_name, element_dir)
    element_home = os.path.join(element_dir, element_name)
    os.mkdir(element_home)
    deps_path = os.path.join(element_home, 'element-deps')

    with open(deps_path, 'w') as deps_file:
        deps_file.write("\n".join(element_deps))
        provides_path = os.path.join(element_home, 'element-provides')

    with open(provides_path, 'w') as provides_file:
        provides_file.write("\n".join(provides))


class TestElementDeps(testtools.TestCase):

    def setUp(self):
        super(TestElementDeps, self).setUp()
        self.element_root_dir = self.useFixture(fixtures.TempDir()).path

        self.element_dir = os.path.join(self.element_root_dir, 'elements')
        self.element_override_dir = os.path.join(self.element_root_dir,
                                                 'element-override')
        os.mkdir(self.element_dir)
        os.mkdir(self.element_override_dir)

        self.log_fixture = self.useFixture(
            fixtures.FakeLogger(level=logging.DEBUG))
        _populate_element(self.element_dir, 'requires-foo', ['foo'])
        _populate_element(self.element_dir,
                          'foo',
                          [],
                          ['operating-system'])
        _populate_element(self.element_dir,
                          'requires-requires-foo',
                          ['requires-foo'])
        _populate_element(self.element_dir, 'self', ['self'])
        _populate_element(self.element_dir,
                          'provides_virtual',
                          [],
                          ['virtual'])
        _populate_element(self.element_dir,
                          'requires_virtual',
                          ['virtual'],
                          ['operating-system'])
        _populate_element(self.element_dir, 'virtual', ['extra_dependency'])
        _populate_element(self.element_dir, 'extra_dependency', [])
        _populate_element(self.element_dir,
                          'circular1',
                          ['circular2'],
                          ['operating-system'])
        _populate_element(self.element_dir, 'circular2', ['circular1'])
        _populate_element(self.element_dir,
                          'provides_new_virtual',
                          [],
                          ['new_virtual', 'operating-system'])
        _populate_element(self.element_dir,
                          'requires_new_virtual',
                          ['new_virtual'])

        # second element should override the first one here
        _populate_element(self.element_dir, 'override_element', [])
        _populate_element(self.element_override_dir, 'override_element', [])

        # This simulates $ELEMENTS_PATH
        self.element_dirs = "%s:%s" % (self.element_override_dir,
                                       self.element_dir)

    # helper to return an (element, path) tuple from the standard dir
    def _e(self, element):
        return (element, os.path.join(self.element_dir, element))

    # helper to return an (element, path) tuple from the override dir
    def _eo(self, element):
        return (element, os.path.join(self.element_override_dir, element))

    def test_non_transitive_deps(self):
        result = element_dependencies.get_elements(['requires-foo'],
                                                   self.element_dirs)
        self.assertItemsEqual([self._e('foo'), self._e('requires-foo')],
                              result)

    def test_missing_deps(self):
        e = self.assertRaises(element_dependencies.MissingElementException,
                              element_dependencies.get_elements,
                              ['fake'],
                              self.element_dirs)
        self.assertIn("Element 'fake' not found", str(e))

    def test_invalid_element_dir(self):
        e = self.assertRaises(element_dependencies.InvalidElementDir,
                              element_dependencies.get_elements,
                              ['fake'],
                              self.element_dirs + ":/not/a/dir")
        self.assertIn("ELEMENTS_PATH entry '/not/a/dir' is not a directory",
                      str(e))

    def test_transitive_deps(self):
        result = element_dependencies.get_elements(
                ['requires-requires-foo'], self.element_dirs)

        self.assertItemsEqual([self._e('requires-requires-foo'),
                               self._e('requires-foo'),
                               self._e('foo')], result)

    def test_no_deps(self):
        result = element_dependencies.get_elements(['foo'], self.element_dirs)
        self.assertEqual([self._e('foo')], result)

    def test_self(self):
        result = element_dependencies.get_elements(['self', 'foo'],
                                                   self.element_dirs)
        self.assertItemsEqual([self._e('self'),
                               self._e('foo')], result)

    def test_circular(self):
        result = element_dependencies.get_elements(['circular1'],
                                                   self.element_dirs)
        self.assertItemsEqual([self._e('circular1'),
                               self._e('circular2')], result)

    def test_provide(self):
        result = element_dependencies.get_elements(
                ['provides_virtual', 'requires_virtual'],
                self.element_dirs)
        self.assertItemsEqual([self._e('requires_virtual'),
                               self._e('provides_virtual')], result)

    def test_provide_conflict(self):
        self.assertRaises(element_dependencies.AlreadyProvidedException,
                          element_dependencies.get_elements,
                                  ['virtual', 'provides_virtual'],
                                  self.element_dirs)

    def test_provide_virtual_ordering(self):
        result = element_dependencies.get_elements(
                ['requires_new_virtual', 'provides_new_virtual'],
                self.element_dirs)
        self.assertItemsEqual(
                [self._e('requires_new_virtual'),
                 self._e('provides_new_virtual')], result)

    def test_no_os_element(self):
        self.assertRaises(element_dependencies.MissingOSException,
                          element_dependencies.get_elements,
                          ['provides_virtual'],
                          self.element_dirs)

    def test_duplicated_os_passed_as_element(self):
        self.assertRaises(
                element_dependencies.AlreadyProvidedException,
                element_dependencies.get_elements,
                ['circular1', 'operating-system'],
                self.element_dirs)
        # ensure we get the error message about what's providing the
        # conflicting package
        self.assertIn("operating-system : already provided by ['circular1']",
                      self.log_fixture.output)

    def test_element_override(self):
        # make sure we picked up "override_element" from the override dir,
        # not the base dir
        result = element_dependencies.get_elements(['override_element', 'foo'],
                                                   self.element_dirs)
        self.assertItemsEqual([self._e('foo'),
                               self._eo('override_element')],
                              result)

    def test_expand_dependencies_deprecated(self):
        # test the deprecated expand_dependencies call
        result = element_dependencies.expand_dependencies(
                ['foo', 'requires-foo'], self.element_dirs)
        self.assertItemsEqual(['foo', 'requires-foo'], result)

    def test_output_sanity(self):
        # very basic output sanity test
        elements = element_dependencies._get_elements(['foo', 'requires-foo'],
                                                      self.element_dirs)
        element_dependencies._output_env_vars(elements)


class TestElements(testtools.TestCase):
    def test_depends_on_env(self):
        self.useFixture(
            fixtures.EnvironmentVariable('ELEMENTS_PATH', '/foo/bar'))
        self.assertEqual('/foo/bar',
                         element_dependencies._get_elements_dir())

    def test_env_not_set(self):
        self.useFixture(fixtures.EnvironmentVariable('ELEMENTS_PATH', ''))
        self.assertRaises(Exception,
                          element_dependencies._get_elements_dir, ())
