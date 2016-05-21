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
import sys


logger = logging.getLogger(__name__)


class LevelBase(object):

    def __init__(self, lvl, config, default_config, result, sub_modules):
        self.level = lvl
        self.config = config
        self.default_config = default_config
        self.result = result
        self.sub_modules = sub_modules

    def call_sub_modules(self, callback):
        """Generic way calling submodules"""
        result = {}
        if self.result is not None:
            result = self.result.copy()
        for name, cfg in self.config:
            if name in self.sub_modules:
                logger.info("Calling sub module [%s]" % name)
                sm = self.sub_modules[name](cfg, self.default_config,
                                            self.result)
                lres = callback(sm)
                result.update(lres)
            else:
                logger.error("Unknown sub module [%s]" % name)
                sys.exit(1)
        return result

    def create_cb(self, obj):
        return obj.create()

    def create(self):
        """Create the configured block devices"""
        logger.info("Starting to create level [%d] block devices" % self.level)
        result = self.call_sub_modules(self.create_cb)
        logger.info("Finished creating level [%d] block devices" % self.level)
        return result

    def delete_cb(self, obj):
        return obj.delete()

    def delete(self):
        """Delete the configured block devices"""
        logger.info("Starting to delete level [%d] block devices" % self.level)
        res = self.call_sub_modules(self.delete_cb)
        logger.info("Finished deleting level [%d] block devices" % self.level)
        return all(p for p in res.values())
