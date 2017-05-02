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

    def generate_phase_doc(self):
        phase_doc = ""
        bdattrs = dir(BlockDevice)
        for attr in bdattrs:
            if attr.startswith("cmd_"):
                phase_doc += "  '" + attr[4:] + "'\n"
                method = getattr(BlockDevice, attr, None)
                # The first line is the line that is used
                phase_doc += "    " + method.__doc__.split("\n")[0] + "\n"
        return phase_doc

    def main(self):
        logging_config.setup()
        phase_doc = self.generate_phase_doc()

        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="Create block device layer",
            epilog="Available phases:\n" + phase_doc)
        parser.add_argument('--phase', required=True,
                            help="phase to execute")
        parser.add_argument('--params', required=False,
                            help="YAML file containing parameters for "
                            "block-device handling.  Default is "
                            "DIB_BLOCK_DEVICE_PARAMS_YAML")
        parser.add_argument('--symbol', required=False,
                            help="symbol to query for getval")
        args = parser.parse_args()

        # Find, open and parse the parameters file
        if not args.params:
            if 'DIB_BLOCK_DEVICE_PARAMS_YAML' in os.environ:
                param_file = os.environ['DIB_BLOCK_DEVICE_PARAMS_YAML']
            else:
                parser.error(
                    "DIB_BLOCK_DEVICE_PARAMS_YAML or --params not set")
        else:
            param_file = args.params
            logger.info("params [%s]" % param_file)
        try:
            with open(param_file) as f:
                params = yaml.safe_load(f)
        except Exception:
            logger.exception("Failed to open parameter YAML")
            sys.exit(1)

        logger.info("phase [%s]" % args.phase)

        if args.symbol:
            logger.info("symbol [%s]" % args.symbol)

        bd = BlockDevice(params, args)

        # Check if the method is available
        method = getattr(bd, "cmd_" + args.phase, None)
        if callable(method):
            # If so: call it.
            return method()
        else:
            logger.error("phase [%s] does not exists" % args.phase)
            return 1


def main():
    bdc = BlockDeviceCmd()
    return bdc.main()

if __name__ == "__main__":
    sys.exit(main())
