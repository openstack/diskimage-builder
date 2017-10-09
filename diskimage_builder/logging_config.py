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

# Python Logging Configuration for DIB
# Usage:
# In the main (application) file, do an
#   import logging_config
#   ...
#   logging_config.setup()
# It is then possible to use the normal python logging interface, like
#   logger = logging.getLogger(__name__)
#   logger.info("Info Message")

import json
import logging
import logging.config
import os
import sys


# A simple formatter to more or less copy oslo.log's ContextFormatter
class DibFormatter(logging.Formatter):

    def __init__(self, *args, **kwargs):
        self.fmt = kwargs['fmt']
        self.debug_suffix = kwargs.pop('debug_suffix')
        logging.Formatter.__init__(self, *args, **kwargs)

    def format(self, record):
        if record.levelno == logging.DEBUG:
            fmt = self.fmt + self.debug_suffix
        else:
            fmt = self.fmt

        if sys.version_info < (3, 2):
            self._fmt = fmt
        else:
            self._style = logging.PercentStyle(fmt)
            self._fmt = self._style._fmt

        return logging.Formatter.format(self, record)


def setup():
    # Check for the DIB_DEBUG_TRACE environment variable
    # If it is set to something greater then 0, use debug
    # logging.
    LOG_LEVEL = "DEBUG" if 'DIB_DEBUG_TRACE' in os.environ \
                and int(os.environ['DIB_DEBUG_TRACE']) > 0 else "INFO"

    # Default logging configuration which can be overwritten
    # by a config file passed in by a user.
    PYTHON_LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,

        # note that disk-image-create runs stdout through
        # outfilter.py, which adds the timestamp.  this doesn't have a
        # timestamp to avoid double logging
        'formatters': {
            'standard': {
                '()': 'diskimage_builder.logging_config.DibFormatter',
                'fmt': '%(levelname)s '
                '%(name)s [-] %(message)s',
                'debug_suffix': ' %(funcName)s %(pathname)s:%(lineno)d'
            }
        },
        'handlers': {
            'default': {
                'level': LOG_LEVEL,
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
            }
        },
        'loggers': {
            '': {
                'handlers': ['default'],
                'level': LOG_LEVEL,
                'propagate': True
            }
        }
    }

    if 'DIB_PYTHON_LOGGING_CONFIG_FILE' in os.environ:
        with open(os.environ['DIB_PYTHON_LOGGING_CONFIG_FILE']) as fd:
            PYTHON_LOGGING_CONFIG = json.load(fd)

    logging.config.dictConfig(PYTHON_LOGGING_CONFIG)
