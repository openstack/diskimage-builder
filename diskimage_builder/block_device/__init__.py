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
from diskimage_builder.block_device.blockdevice import BlockDevice
from diskimage_builder import logging_config
import logging


def val_else_none(s):
    return s if s is None or len(s) > 0 else None


def generate_phase_doc():
    phase_doc = ""
    bdattrs = dir(BlockDevice)
    for attr in bdattrs:
        if attr.startswith("cmd_"):
            phase_doc += "  '" + attr[4:] + "'\n"
            method = getattr(BlockDevice, attr, None)
            # The first line is the line that is used
            phase_doc += "    " + method.__doc__.split("\n")[0] + "\n"
    return phase_doc


def main():
    logging_config.setup()
    logger = logging.getLogger(__name__)
    phase_doc = generate_phase_doc()

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Create block device layer",
        epilog="Available phases:\n" + phase_doc)
    parser.add_argument('--phase', required=True,
                        help="phase to execute")
    parser.add_argument('--params', required=True,
                        help="parameters for block device handling")
    parser.add_argument('--symbol', required=False,
                        help="symbol to query for getval")
    args = parser.parse_args()

    logger.info("phase [%s]" % args.phase)
    logger.info("params [%s]" % args.params)
    if args.symbol:
        logger.info("symbol [%s]" % args.symbol)

    bd = BlockDevice(args)

    # Check if the method is available
    method = getattr(bd, "cmd_" + args.phase, None)
    if callable(method):
        # If so: call it.
        return method()
    else:
        logger.error("phase [%s] does not exists" % args.phase)
        return 1

    return 0

if __name__ == "__main__":
    main()
