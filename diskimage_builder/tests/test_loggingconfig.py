# Copyright 2016 Andreas Florath (andreas@florath.net)
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

import fixtures
import logging
import testtools

from diskimage_builder import logging_config


class TestLoggingConfig(testtools.TestCase):

    def test_defaults(self):
        self.out = self.useFixture(fixtures.StringStream('stdout'))
        self.useFixture(
            fixtures.MonkeyPatch('sys.stdout', self.out.stream))

        self.err = self.useFixture(fixtures.StringStream('stderr'))
        self.useFixture(
            fixtures.MonkeyPatch('sys.stderr', self.err.stream))

        self.useFixture(fixtures.EnvironmentVariable('DIB_DEBUG_TRACE', '1'))

        logging_config.setup()
        log = logging.getLogger(__name__)
        log.debug("Debug Message")
        self.assertIn("Debug Message", self.err._details["stderr"].as_text())
        # The follow two are looking for the function name / file name
        # suffix we log only for debug messages
        self.assertIn("test_defaults", self.err._details["stderr"].as_text())
        self.assertIn("test_loggingconfig.py",
                      self.err._details["stderr"].as_text())
        log.info("Info Message")
        self.assertIn("Info Message", self.err._details["stderr"].as_text())
        log.warning("Warning Message")
        self.assertIn("Warning Message", self.err._details["stderr"].as_text())
        log.error("Error Message")
        self.assertIn("Error Message", self.err._details["stderr"].as_text())
