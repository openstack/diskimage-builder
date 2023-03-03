# Copyright 2023 Red Hat, Inc.
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
import collections
import io
import jsonschema
import os
import os.path
import shlex
import subprocess
import sys
import textwrap
import yaml

import diskimage_builder.paths


class SchemaProperty(object):
    """Base class for a basic schema and a help string"""

    key = None
    description = None
    schema_type = "string"

    def __init__(self, key, description, schema_type=None):
        self.key = key
        self.description = description
        if schema_type:
            self.schema_type = schema_type

    def to_schema(self):
        return {self.key: {"type": self.schema_type}}

    def type_help(self):
        return "Value is a string"

    def to_help(self):
        return "%s\n%s\n%s\n(%s)" % (
            self.key,
            "-" * len(self.key),
            "\n".join(textwrap.wrap(self.description)),
            self.type_help(),
        )


class Env(SchemaProperty):
    """String dict schema for environment variables"""

    def __init__(self, key, description):
        super(Env, self).__init__(key, description, schema_type="object")

    def to_schema(self):
        schema = super(Env, self).to_schema()
        schema[self.key]["additionalProperties"] = {"type": "string"}
        return schema

    def type_help(self):
        return "Value is a map of strings"


class Arg(SchemaProperty):
    """Command argument with associated value"""

    arg = None

    def __init__(self, key, description, schema_type=None, arg=None):
        super(Arg, self).__init__(key, description, schema_type=schema_type)
        self.arg = arg

    def arg_name(self):
        if self.arg is None:
            return "--%s" % self.key
        return self.arg

    def to_argument(self, value=None):
        arg = self.arg_name()
        if value is not None and value != "":
            return [arg, value]
        return []


class Flag(Arg):
    """Boolean value which does not contribute to arguments"""

    def __init__(self, key, description):
        super(Flag, self).__init__(key, description, schema_type="boolean")

    def to_argument(self, value=None):
        return []

    def type_help(self):
        return "Value is a boolean"


class ArgFlag(Arg):
    """Boolean value for a flag argument being set or not"""

    def __init__(self, key, description, arg=None):
        super(ArgFlag, self).__init__(
            key, description, arg=arg, schema_type="boolean"
        )

    def to_argument(self, value=None):
        if value:
            return [self.arg_name()]
        return []

    def type_help(self):
        return "Value is a boolean"


class ArgEnum(Arg):
    """String argument constrained to a list of allowed values"""

    enum = None

    def __init__(
        self, key, description, schema_type="string", arg=None, enum=None
    ):
        super(ArgEnum, self).__init__(
            key, description, schema_type=schema_type, arg=arg
        )
        self.enum = enum and enum or []

    def to_schema(self):
        schema = super(ArgEnum, self).to_schema()
        schema[self.key]["enum"] = self.enum
        return schema

    def type_help(self):
        return "Allowed values: %s" % ", ".join(self.enum)


class ArgFlagRepeating(ArgEnum):
    """Flag argument which repeats the specified number of times"""

    def __init__(self, key, description, arg=None, max_repeat=0):
        enum = list(range(max_repeat + 1))
        super(ArgFlagRepeating, self).__init__(
            key, description, schema_type="integer", arg=arg, enum=enum
        )

    def to_argument(self, value):
        return [self.arg] * value

    def type_help(self):
        return "Allowed values: %s" % ", ".join([str(i) for i in self.enum])


class ArgInt(Arg):
    """Integer argument which a minumum constraint"""

    minimum = 1

    def __init__(self, key, description, arg=None, minimum=1):
        super(ArgInt, self).__init__(
            key, description, arg=arg, schema_type="integer"
        )
        self.minimum = minimum

    def to_schema(self):
        schema = super(ArgInt, self).to_schema()
        schema[self.key]["minimum"] = self.minimum
        return schema

    def to_argument(self, value):
        return super(ArgInt, self).to_argument(str(value))

    def type_help(self):
        return "Value is an integer"


class ArgList(Arg):
    """List of strings converted to comma delimited argument"""

    def __init__(self, key, description, arg=None):
        super(ArgList, self).__init__(
            key, description, arg=arg, schema_type="array"
        )

    def to_schema(self):
        schema = super(ArgList, self).to_schema()
        schema[self.key]["items"] = {"type": "string"}
        return schema

    def to_argument(self, value):
        if not value:
            return []
        return super(ArgList, self).to_argument(",".join(value))

    def type_help(self):
        return "Value is a list of strings"


class ArgListPositional(ArgList):
    """List of strings converted to positional arguments"""

    def __init__(self, key, description):
        super(ArgListPositional, self).__init__(key, description)

    def to_argument(self, value):
        # it is already a list, just return it
        return value

    def type_help(self):
        return "Value is a list of strings"


class ArgEnumList(ArgList):
    """List of strings constrained to a list of allowed values"""

    enum = None

    def __init__(self, key, description, arg=None, enum=None):
        super(ArgEnumList, self).__init__(key, description, arg=arg)
        self.enum = enum and enum or []

    def to_schema(self):
        schema = super(ArgEnumList, self).to_schema()
        schema[self.key]["items"]["enum"] = self.enum
        return schema

    def type_help(self):
        return (
            "Value is a list of strings with allowed values: %s)"
            % ", ".join(self.enum)
        )


class ArgDictToString(Arg):
    """Dict with string values converted to key=value,key2=value2 argument"""

    def __init__(self, key, description, arg=None):
        super(ArgDictToString, self).__init__(
            key, description, arg=arg, schema_type="object"
        )

    def to_schema(self):
        schema = super(ArgDictToString, self).to_schema()
        schema[self.key]["additionalProperties"] = {"type": "string"}
        return schema

    def to_argument(self, value):
        as_list = []
        for k, v in value.items():
            as_list.append("%s=%s" % (k, v))
        return super(ArgDictToString, self).to_argument(",".join(as_list))

    def type_help(self):
        return "Value is a map of strings"


PROPERTIES = [
    Arg("imagename", "Set the imagename of the output image file.", arg="-o"),
    ArgEnum(
        "arch",
        "Set the architecture of the image.",
        arg="-a",
        enum=[
            "aarch64",
            "amd64",
            "arm64",
            "armhf",
            "powerpc",
            "ppc64",
            "ppc64el",
            "ppc64le",
            "s390x",
            "x86_64",
        ],
    ),
    ArgEnumList(
        "types",
        "Set the image types of the output image files.",
        arg="-t",
        enum=[
            "qcow2",
            "tar",
            "tgz",
            "squashfs",
            "vhd",
            "docker",
            "aci",
            "raw",
        ],
    ),
    Env(
        "environment",
        "Environment variables to set during the image build.",
    ),
    Flag(
        "ramdisk",
        "Whether to build a ramdisk image.",
    ),
    ArgFlagRepeating(
        "debug-trace",
        "Tracing level to log, integer 0 is off.",
        arg="-x",
        max_repeat=2,
    ),
    ArgFlag(
        "uncompressed",
        "Do not compress the image - larger but faster.",
        arg="-u",
    ),
    ArgFlag("clear", "Clear environment before starting work.", arg="-c"),
    Arg(
        "logfile",
        "Save run output to given logfile.",
    ),
    ArgFlag(
        "checksum",
        "Generate MD5 and SHA256 checksum files for the created image.",
    ),
    ArgInt(
        "image-size",
        "Image size in GB for the created image.",
    ),
    ArgInt(
        "image-extra-size",
        "Extra image size in GB for the created image.",
    ),
    Arg(
        "image-cache",
        "Location for cached images, defaults to ~/.cache/image-create.",
    ),
    ArgInt(
        "max-online-resize",
        "Max number of filesystem blocks to support when resizing. "
        "Useful if you want a really large root partition when the "
        "image is deployed. Using a very large value may run into a "
        "known bug in resize2fs. Setting the value to 274877906944 "
        "will get you a 1PB root file system. Making this "
        "value unnecessarily large will consume extra disk "
        "space on the root partition with extra file system inodes.",
    ),
    ArgInt(
        "min-tmpfs",
        "Minimum size in GB needed in tmpfs to build the image.",
    ),
    ArgInt(
        "mkfs-journal-size",
        "Filesystem journal size in MB to pass to mkfs.",
    ),
    Arg(
        "mkfs-options",
        "Option flags to be passed directly to mkfs.",
    ),
    ArgFlag("no-tmpfs", "Do not use tmpfs to speed image build."),
    ArgFlag("offline", "Do not update cached resources."),
    ArgDictToString(
        "qemu-img-options",
        "Option flags to be passed directly to qemu-img.",
    ),
    Arg(
        "root-label",
        'Label for the root filesystem, defaults to "cloudimg-rootfs".',
    ),
    Arg(
        "ramdisk-element",
        "Specify the main element to be used for building ramdisks. "
        'Defaults to "ramdisk".  Should be set to "dracut-ramdisk" '
        "for platforms such as RHEL and CentOS that do not package busybox.",
    ),
    ArgEnum(
        "install-type",
        "Specify the default installation type.",
        enum=["source", "package"],
    ),
    Arg(
        "docker-target",
        "Specify the repo and tag to use if the output type is docker, "
        "defaults to the value of output imagename.",
    ),
    ArgList(
        "packages",
        "Extra packages to install in the image.  Runs once, after "
        '"install.d" phase. Does not apply when ramdisk is true.',
        arg="-p",
    ),
    ArgFlag(
        "skip-base",
        'Skip the default inclusion of the "base" element. '
        "Does not apply when ramdisk is true.",
        arg="-n",
    ),
    ArgListPositional(
        "elements",
        "list of elements to build the image with",
    ),
]


SCHEMA_PROPERTIES = {}
for arg in PROPERTIES:
    SCHEMA_PROPERTIES.update(arg.to_schema())

DIB_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": SCHEMA_PROPERTIES,
        "additionalProperties": False,
    },
    "additionalProperties": False,
}


class Command(object):
    script = None
    args = None
    environ = None

    def __init__(self, script, properties, entry):
        self.script = script
        self.args = []
        self.environ = {}
        for prop in properties:
            if prop.key in entry:
                value = entry[prop.key]
                if isinstance(prop, Env):
                    self.environ.update(value)
                elif isinstance(prop, Arg):
                    self.args.extend(prop.to_argument(value))

    def merged_env(self):
        environ = os.environ.copy()
        # pre-seed some paths for the shell script
        environ["_LIB"] = diskimage_builder.paths.get_path("lib")
        environ.update(self.environ)
        return environ

    def command(self):
        return ["bash", self.script] + self.args

    def __repr__(self):
        elements = []
        for k, v in self.environ.items():
            elements.append("%s=%s" % (k, shlex.quote(v)))
        elements.extend([shlex.quote(a) for a in self.command()])
        return " ".join(elements) + "\n"


def help_properties():
    str = io.StringIO()
    for prop in PROPERTIES:
        str.write(prop.to_help())
        str.write("\n\n")
    return str.getvalue()


def get_args():
    description = (
        """\
The file format is YAML which expects a list of image definition maps.

Supported entries for an image definition are:

%s
"""
        % help_properties()
    )
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "files",
        metavar="<filename>",
        nargs="+",
        help="Paths to image build definition YAML files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the disk-image-create, ramdisk-image-create commands and "
        "exit",
    )
    parser.add_argument(
        "--stop-on-failure",
        action="store_true",
        help="Stop building images when an image build fails",
    )
    args = parser.parse_args(sys.argv[1:])
    return args


def merge_entry(merged_entry, entry):
    for k, v in entry.items():
        if isinstance(v, list):
            # append to existing list
            list_value = merged_entry.setdefault(k, [])
            list_value.extend(v)
        elif isinstance(v, dict):
            # update environment dict
            dict_value = merged_entry.setdefault(k, {})
            dict_value.update(v)
        else:
            # update value
            merged_entry[k] = v


def build_commands(definition):
    jsonschema.validate(definition, schema=DIB_SCHEMA)
    dib_script = "%s/disk-image-create" % diskimage_builder.paths.get_path(
        "lib"
    )
    rib_script = "%s/ramdisk-image-create" % diskimage_builder.paths.get_path(
        "lib"
    )

    # Start with the default image name, 'image'
    previous_imagename = "image"
    merged_entries = collections.OrderedDict()
    for entry in definition:
        imagename = entry.get("imagename", previous_imagename)
        previous_imagename = imagename
        if imagename not in merged_entries:
            merged_entries[imagename] = entry
        else:
            merge_entry(merged_entries[imagename], entry)

    commands = []
    for entry in merged_entries.values():
        if entry.get("ramdisk", False):
            commands.append(Command(rib_script, PROPERTIES, entry))
        else:
            commands.append(Command(dib_script, PROPERTIES, entry))
    return commands


def main():
    args = get_args()

    # export the path to the current python
    if not os.environ.get("DIB_PYTHON_EXEC"):
        os.environ["DIB_PYTHON_EXEC"] = sys.executable

    definitions = []
    for file in args.files:
        with open(file) as f:
            definitions.extend(yaml.safe_load(f))
    commands = build_commands(definitions)
    final_returncode = 0
    failed_command = None
    for command in commands:
        sys.stderr.write(str(command))
        sys.stderr.write("\n")
        sys.stderr.flush()
        if not args.dry_run:
            p = subprocess.Popen(command.command(), env=command.merged_env())
            p.communicate()
            if p.returncode != 0:
                final_returncode = p.returncode
                failed_command = command
                if args.stop_on_failure:
                    break

    if final_returncode != 0:
        raise subprocess.CalledProcessError(
            final_returncode, failed_command.command()
        )
