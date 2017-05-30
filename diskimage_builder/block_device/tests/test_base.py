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

import fixtures
import logging
import os
import testtools
import yaml


logger = logging.getLogger(__name__)


class TestBase(testtools.TestCase):
    """Base for all test cases"""
    def setUp(self):
        super(TestBase, self).setUp()

        fs = '%(asctime)s %(levelname)s [%(name)s] %(message)s'
        self.log_fixture = self.useFixture(
            fixtures.FakeLogger(level=logging.DEBUG, format=fs))

    def get_config_file(self, f):
        """Get the full path to sample config file f """
        logger.debug(os.path.dirname(__file__))
        return os.path.join(os.path.dirname(__file__), 'config', f)

    def load_config_file(self, f):
        """Load f and return it after yaml parsing"""
        path = self.get_config_file(f)
        with open(path, 'r') as config:
            return yaml.safe_load(config)
