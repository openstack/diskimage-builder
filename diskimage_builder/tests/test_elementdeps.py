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

import os

import fixtures
import testtools

from diskimage_builder import element_dependencies

data_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'test-elements'))


def _populate_element(element_dir, element_name, element_deps=[], provides=[]):
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
        self.element_dir = self.useFixture(fixtures.TempDir()).path
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

    def test_non_transitive_deps(self):
        result = element_dependencies.expand_dependencies(
            ['requires-foo'],
            elements_dir=self.element_dir)
        self.assertEqual(set(['requires-foo', 'foo']), result)

    def test_missing_deps(self):
        self.assertRaises(SystemExit,
                          element_dependencies.expand_dependencies, ['fake'],
                          self.element_dir)

    def test_transitive_deps(self):
        result = element_dependencies.expand_dependencies(
            ['requires-requires-foo'], elements_dir=self.element_dir)
        self.assertEqual(set(['requires-requires-foo',
                              'requires-foo',
                              'foo']), result)

    def test_no_deps(self):
        result = element_dependencies.expand_dependencies(
            ['foo'], elements_dir=self.element_dir)
        self.assertEqual(set(['foo']), result)

    def test_self(self):
        result = element_dependencies.expand_dependencies(
            ['self', 'foo'], elements_dir=self.element_dir)
        self.assertEqual(set(['self', 'foo']), result)

    def test_circular(self):
        result = element_dependencies.expand_dependencies(
            ['circular1'], elements_dir=self.element_dir)
        self.assertEqual(set(['circular1', 'circular2']), result)

    def test_provide(self):
        result = element_dependencies.expand_dependencies(
            ['provides_virtual', 'requires_virtual'],
            elements_dir=self.element_dir)
        self.assertEqual(set(['requires_virtual', 'provides_virtual']), result)

    def test_provide_conflict(self):
        self.assertRaises(SystemExit,
                          element_dependencies.expand_dependencies,
                          ['virtual', 'provides_virtual'],
                          self.element_dir)

    def test_provide_virtual_ordering(self):
        result = element_dependencies.expand_dependencies(
            ['requires_new_virtual', 'provides_new_virtual'],
            elements_dir=self.element_dir)
        self.assertEqual(set(['requires_new_virtual', 'provides_new_virtual']),
                         result)

    def test_no_os_element(self):
        self.assertRaises(SystemExit,
                          element_dependencies.expand_dependencies,
                          ['provides_virtual'],
                          elements_dir=self.element_dir)

    def test_duplicated_os_passed_as_element(self):
        self.assertRaises(SystemExit,
                          element_dependencies.expand_dependencies,
                          ['circular1', 'operating-system'],
                          elements_dir=self.element_dir)


class TestElements(testtools.TestCase):
    def test_depends_on_env(self):
        self.useFixture(
            fixtures.EnvironmentVariable('ELEMENTS_PATH', '/foo/bar'))
        self.assertEqual('/foo/bar', element_dependencies.get_elements_dir())

    def test_env_not_set(self):
        self.useFixture(fixtures.EnvironmentVariable('ELEMENTS_PATH', ''))
        self.assertRaises(Exception, element_dependencies.get_elements_dir, ())
