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

import codecs
import fixtures
import json
import logging
import os

from stevedore import extension
from testtools.matchers import FileExists

import diskimage_builder.block_device.blockdevice as bd
import diskimage_builder.block_device.tests.test_base as tb

from diskimage_builder.block_device.exception import \
    BlockDeviceSetupException

logger = logging.getLogger(__name__)


class TestStateBase(tb.TestBase):

    def setUp(self):
        super(TestStateBase, self).setUp()

        # override the extensions to the test extensions
        test_extensions = extension.ExtensionManager(
            namespace='diskimage_builder.block_device.plugin_test',
            invoke_on_load=False)
        extensions_fixture = fixtures.MonkeyPatch(
            'diskimage_builder.block_device.config._extensions',
            test_extensions)
        self.useFixture(extensions_fixture)

        # status and other bits saved here
        self.build_dir = fixtures.TempDir()
        self.useFixture(self.build_dir)


class TestState(TestStateBase):

    # The the state generation & saving methods
    def test_state_create(self):
        params = {
            'build-dir': self.build_dir.path,
            'config': self.get_config_file('cmd_create.yaml')
        }

        bd_obj = bd.BlockDevice(params)

        bd_obj.cmd_init()
        bd_obj.cmd_create()

        # cmd_create should have persisted this to disk
        state_file = bd_obj.state_json_file_name
        self.assertThat(state_file, FileExists())

        # ensure we see the values put in by the test extensions
        # persisted
        with codecs.open(state_file, encoding='utf-8', mode='r') as fd:
            state = json.load(fd)
        self.assertDictEqual(state,
                             {'test_a': {'value': 'foo',
                                         'value2': 'bar'},
                              'test_b': {'value': 'baz'},
                              'test_init_state': 'here'})

        pickle_file = bd_obj.node_pickle_file_name
        self.assertThat(pickle_file, FileExists())

        # run umount, which should load the picked nodes and run in
        # reverse.  This will create some state in "test_b" that it
        # added to by "test_a" ... ensuring it was run backwards.  It
        # also checks the state was persisted through the pickling
        # process.
        bd_obj.cmd_umount()

    # Test state going missing between phases
    def test_missing_state(self):
        params = {
            'build-dir': self.build_dir.path,
            'config': self.get_config_file('cmd_create.yaml')
        }

        bd_obj = bd.BlockDevice(params)
        bd_obj.cmd_init()
        bd_obj.cmd_create()

        # cmd_create should have persisted this to disk
        state_file = bd_obj.state_json_file_name
        self.assertThat(state_file, FileExists())
        pickle_file = bd_obj.node_pickle_file_name
        self.assertThat(pickle_file, FileExists())

        # simulate the state somehow going missing, and ensure that
        # later calls notice
        os.unlink(state_file)
        os.unlink(pickle_file)
        # This reads from the state dump json file
        self.assertRaisesRegex(BlockDeviceSetupException,
                               "State dump not found",
                               bd_obj.cmd_getval, 'image-path')
        self.assertRaisesRegex(BlockDeviceSetupException,
                               "State dump not found",
                               bd_obj.cmd_writefstab)

        # this uses the pickled nodes
        self.assertRaisesRegex(BlockDeviceSetupException,
                               "Pickle file not found",
                               bd_obj.cmd_delete)
        self.assertRaisesRegex(BlockDeviceSetupException,
                               "Pickle file not found",
                               bd_obj.cmd_cleanup)

        # XXX: figure out unit test for umount

    # Test ordering of rollback calls if create() fails
    def test_rollback(self):
        params = {
            'build-dir': self.build_dir.path,
            'config': self.get_config_file('rollback.yaml'),
            'test_rollback': True
        }

        bd_obj = bd.BlockDevice(params)
        bd_obj.cmd_init()

        # The config file has flags in that tell the last node to
        # fail, which will trigger the rollback.
        self.assertRaises(RuntimeError, bd_obj.cmd_create)

        # cmd_create should have persisted this to disk even after the
        # failure
        state_file = bd_obj.state_json_file_name
        self.assertThat(state_file, FileExists())
        with codecs.open(state_file, encoding='utf-8', mode='r') as fd:
            state = json.load(fd)

        # ensure the rollback was called in order
        self.assertListEqual(state['rollback_test'],
                             ['never', 'gonna', 'give', 'you', 'up',
                              'never', 'gonna', 'let', 'you', 'down'])
