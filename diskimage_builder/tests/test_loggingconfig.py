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

import logging
import testtools

from diskimage_builder import logging_config


class TestLoggingConfig(testtools.TestCase):

    def test_defaults(self):
        logging_config.setup()
        log = logging.getLogger(__name__)
        log.debug("Debug Message")
        log.info("Info Message")
        log.warning("Warning Message")
        log.error("Error Message")
