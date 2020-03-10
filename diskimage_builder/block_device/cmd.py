# Copyright 2016-2017 Andreas Florath (andreas@florath.net)
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

import argparse
import logging
import os
import sys
import yaml

from diskimage_builder.block_device.blockdevice import BlockDevice
from diskimage_builder import logging_config

logger = logging.getLogger(__name__)


class BlockDeviceCmd(object):

    def cmd_init(self):
        self.bd.cmd_init()

    def cmd_getval(self):
        self.bd.cmd_getval(self.args.symbol)

    def cmd_create(self):
        self.bd.cmd_create()

    def cmd_umount(self):
        self.bd.cmd_umount()

    def cmd_cleanup(self):
        self.bd.cmd_cleanup()

    def cmd_delete(self):
        self.bd.cmd_delete()

    def cmd_writefstab(self):
        self.bd.cmd_writefstab()

    def main(self):
        logging_config.setup()

        parser = argparse.ArgumentParser(description="DIB Block Device helper")
        parser.add_argument('--params', required=False,
                            help="YAML file containing parameters for "
                            "block-device handling.  Default is "
                            "DIB_BLOCK_DEVICE_PARAMS_YAML")

        subparsers = parser.add_subparsers(title='commands',
                                           description='valid commands',
                                           dest='command',
                                           help='additional help')

        cmd_init = subparsers.add_parser('init',
                                         help='Initialize configuration')
        cmd_init.set_defaults(func=self.cmd_init)

        cmd_getval = subparsers.add_parser('getval',
                                           help='Retrieve information about '
                                           'internal state')
        cmd_getval.set_defaults(func=self.cmd_getval)
        cmd_getval.add_argument('symbol', help='symbol to print')

        cmd_create = subparsers.add_parser('create',
                                           help='Create the block device')
        cmd_create.set_defaults(func=self.cmd_create)

        cmd_umount = subparsers.add_parser('umount',
                                           help='Unmount blockdevice and '
                                           'cleanup resources')
        cmd_umount.set_defaults(func=self.cmd_umount)

        cmd_cleanup = subparsers.add_parser('cleanup', help='Final cleanup')
        cmd_cleanup.set_defaults(func=self.cmd_cleanup)

        cmd_delete = subparsers.add_parser('delete', help='Error cleanup')
        cmd_delete.set_defaults(func=self.cmd_delete)

        cmd_writefstab = subparsers.add_parser('writefstab',
                                               help='Create fstab for system')
        cmd_writefstab.set_defaults(func=self.cmd_writefstab)

        self.args = parser.parse_args()

        # Find, open and parse the parameters file
        if not self.args.params:
            if 'DIB_BLOCK_DEVICE_PARAMS_YAML' in os.environ:
                param_file = os.environ['DIB_BLOCK_DEVICE_PARAMS_YAML']
            else:
                parser.error(
                    "DIB_BLOCK_DEVICE_PARAMS_YAML or --params not set")
        else:
            param_file = self.args.params
            logger.info("params [%s]", param_file)
        try:
            with open(param_file) as f:
                self.params = yaml.safe_load(f)
        except Exception:
            logger.exception("Failed to open parameter YAML")
            sys.exit(1)

        # Setup main BlockDevice object from args
        self.bd = BlockDevice(self.params)

        self.args.func()


def main():
    bdc = BlockDeviceCmd()
    return bdc.main()


if __name__ == "__main__":
    sys.exit(main())
