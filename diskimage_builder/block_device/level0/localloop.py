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

from diskimage_builder.block_device.utils import parse_abs_size_spec
import logging
import os
import subprocess
import sys
import time


logger = logging.getLogger(__name__)


class LocalLoop(object):
    """Level0: Local loop image device handling.

    This class handles local loop devices that can be used
    for VM image installation.
    """

    type_string = "local_loop"

    def __init__(self, config, default_config, result=None):
        if 'size' in config:
            self.size = parse_abs_size_spec(config['size'])
            logger.debug("Image size [%s]" % self.size)
        else:
            self.size = parse_abs_size_spec(default_config['image_size'])
            logger.debug("Using default image size [%s]" % self.size)
        if 'directory' in config:
            self.image_dir = config['directory']
        else:
            self.image_dir = default_config['image_dir']
        self.name = config['name']
        self.filename = os.path.join(self.image_dir, self.name + ".raw")
        self.result = result
        if self.result is not None:
            self.block_device = self.result[self.name]['device']

    def create(self):
        logger.debug("[%s] Creating loop on [%s] with size [%d]" %
                     (self.name, self.filename, self.size))

        with open(self.filename, "w") as fd:
            fd.seek(self.size - 1)
            fd.write("\0")

        logger.debug("Calling [sudo losetup --show -f %s]"
                     % self.filename)
        subp = subprocess.Popen(["sudo", "losetup", "--show", "-f",
                                 self.filename], stdout=subprocess.PIPE)
        rval = subp.wait()
        if rval == 0:
            # [:-1]: Cut of the newline
            self.block_device = subp.stdout.read()[:-1]
            logger.debug("New block device [%s]" % self.block_device)
        else:
            logger.error("losetup failed")
            sys.exit(1)

        return {self.name: {"device": self.block_device,
                            "image": self.filename}}

    def delete(self):
        # loopback dev may be tied up a bit by udev events triggered
        # by partition events
        for try_cnt in range(10, 1, -1):
            logger.debug("Delete loop [%s]" % self.block_device)
            res = subprocess.call("sudo losetup -d %s" %
                                  (self.block_device),
                                  shell=True)
            if res == 0:
                return {self.name: True}
            logger.debug("[%s] may be busy, sleeping [%d] more secs"
                         % (self.block_device, try_cnt))
            time.sleep(1)

        logger.debug("Gave up trying to detach [%s]" %
                     self.block_device)
        return {self.name: False}
