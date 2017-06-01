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

import diskimage_builder.block_device.tests.test_config as tc

from diskimage_builder.block_device.config import create_graph
from diskimage_builder.block_device.exception import \
    BlockDeviceSetupException


logger = logging.getLogger(__name__)


class TestMkfs(tc.TestGraphGeneration):

    def test_duplicate_labels(self):

        config = self.load_config_file('duplicate_fs_labels.yaml')

        self.assertRaisesRegex(BlockDeviceSetupException,
                               "used more than once",
                               create_graph, config,
                               self.fake_default_config, {})

    def test_too_long_labels(self):

        config = self.load_config_file('too_long_fs_label.yaml')

        self.assertRaisesRegex(BlockDeviceSetupException,
                               "too long for filesystem",
                               create_graph, config,
                               self.fake_default_config, {})
