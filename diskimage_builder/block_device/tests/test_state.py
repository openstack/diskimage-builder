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
        state_file = os.path.join(self.build_dir.path,
                                  'states', 'block-device',
                                  'state.json')
        self.assertThat(state_file, FileExists())

        # ensure we see the values put in by the test extensions
        # persisted
        with codecs.open(state_file, encoding='utf-8', mode='r') as fd:
            state = json.load(fd)
        self.assertDictEqual(state,
                             {'test_a': {'value': 'foo',
                                         'value2': 'bar'},
                              'test_b': {'value': 'baz'}})

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
        state_file = os.path.join(self.build_dir.path,
                                  'states', 'block-device',
                                  'state.json')
        self.assertThat(state_file, FileExists())

        # simulate the state somehow going missing, and ensure that
        # later calls notice
        os.unlink(state_file)
        self.assertRaisesRegexp(BlockDeviceSetupException,
                                "State dump not found",
                                bd_obj.cmd_cleanup)
        self.assertRaisesRegexp(BlockDeviceSetupException,
                                "State dump not found",
                                bd_obj.cmd_writefstab)
        self.assertRaisesRegexp(BlockDeviceSetupException,
                                "State dump not found",
                                bd_obj.cmd_delete)
