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

from diskimage_builder.block_device.level0.localloop import LocalLoop
from diskimage_builder.block_device.levelbase import LevelBase

__all__ = [LocalLoop]


class Level0(LevelBase):
    """Block Device Level0: preparation of images

    This is the class that handles level 0 block device setup:
    creating the block device image and providing OS access to it.
    """

    def __init__(self, config, default_config, result):
        LevelBase.__init__(self, 0, config, default_config, result,
                           {LocalLoop.type_string: LocalLoop})
