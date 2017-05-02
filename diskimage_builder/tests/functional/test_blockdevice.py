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
import subprocess
import testtools

from diskimage_builder.block_device.blockdevice import BlockDevice
from diskimage_builder.block_device.level0 import localloop
from diskimage_builder.logging_config import setup


# Setup Logging
setup()


class StateSavingBlockDevice(BlockDevice):
    def cmd_create(self):
        logging.info("StateSavingBlockDevice cmd_create()")
        super(StateSavingBlockDevice, self).cmd_create()
        _, _, self.state = self.load_state()


class BlockDeviceFixture(fixtures.Fixture):
    def __init__(self, *args, **kwargs):
        logging.info("BlockDeviceFixture constructor")
        self.args = args
        self.kwargs = kwargs
        self.bd = None

    def _setUp(self):
        logging.info("BlockDeviceFixture _setUp()")
        self.bd = StateSavingBlockDevice(*self.args, **self.kwargs)
        self.addCleanup(self.cleanup_loopbacks)

    def _assert_loopback_detatched(self, loopback):
        if localloop.LocalLoop.loopdev_is_attached(loopback):
            localloop.LocalLoop.loopdev_detach(loopback)

    def cleanup_loopbacks(self):
        for lb_dev in self.bd.state.get('loopback_devices', []):
            self._assert_loopback_detatched(lb_dev)


class TestBlockDevice(testtools.TestCase):
    def _assert_loopbacks_cleaned(self, blockdevice):
        for lb_dev in blockdevice.state.get('loopback_devices', []):
            self.assertEqual(False,
                             localloop.LocalLoop.loopdev_is_attached(lb_dev))

    # ToDo: This calls sudo to setup the loop device - which is not allowed.
    # Currently no idea how to continue here...
    def _DONT_test_create_default_config(self):
        logging.info("test_create_default_config called")
        builddir = self.useFixture(fixtures.TempDir()).path
        imagedir = self.useFixture(fixtures.TempDir()).path
        logging.info("builddir [%s]" % builddir)
        logging.info("imagedir [%s]" % imagedir)

        logging.info("Calling BlockDevice constructor")
        bd = self.useFixture(BlockDeviceFixture(
            None, builddir, '%dKiB' % (1024 * 1024), imagedir
        )).bd
        logging.info("Calling BlockDevice cmd_create()")
        bd.cmd_create()

        logging.info("Check result")
        logging.info("State [%s]" % bd.state)
        self.assertTrue('device' in bd.state['image0'])
        lb_dev = bd.state['image0']['device']
        # partprobe loopback so we can get partition info
        args = ['sudo', 'partprobe', lb_dev]
        logging.info("Call: %s" % args)
        subprocess.check_call(args)
        bd.cmd_cleanup()
        self._assert_loopbacks_cleaned(bd)
