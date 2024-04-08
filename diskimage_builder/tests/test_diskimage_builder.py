# Copyright 2023 Red Hat, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
import subprocess
import tempfile
from unittest import mock

import jsonschema
import testtools
import yaml

from diskimage_builder import diskimage_builder as dib


class TestDib(testtools.TestCase):
    def assert_to_argument(self, expected, prop, value):
        self.assertEqual(expected, prop.to_argument(value))
        self.assert_schema_validate(prop, value)

    def assert_schema_validate(self, prop, value, assert_failure=False):
        # create a fake dict value and validate the schema against it
        value_dict = {prop.key: value}
        schema = {"type": "object", "properties": {}}
        schema["properties"].update(prop.to_schema())
        if assert_failure:
            self.assertRaises(
                jsonschema.exceptions.ValidationError,
                jsonschema.validate,
                value_dict,
                schema=schema,
            )
        else:
            jsonschema.validate(value_dict, schema=schema)

    def test_schema_property(self):
        x = dib.SchemaProperty(
            "the_key", "the description", schema_type="integer"
        )
        self.assertEqual(
            """\
the_key
-------
the description
(Value is a string)""",
            x.to_help(),
        )
        self.assertEqual({"the_key": {"type": "integer"}}, x.to_schema())

    def test_env(self):
        x = dib.Env(
            "environment",
            "environment variables to set during the image build",
        )
        self.assertEqual(
            {
                "environment": {
                    "additionalProperties": {"type": "string"},
                    "type": "object",
                }
            },
            x.to_schema(),
        )

    def test_arg(self):
        # no arg
        x = dib.Arg("the-key", "")
        self.assert_to_argument(["--the-key", "the value"], x, "the value")

        # with arg
        x = dib.Arg("the-key", "", arg="--key")
        self.assert_to_argument(["--key", "the value"], x, "the value")

        # with empty string value
        self.assert_to_argument([], x, "")

    def test_arg_flag(self):
        x = dib.ArgFlag("doit", "do it", arg="-d")
        self.assertEqual({"doit": {"type": "boolean"}}, x.to_schema())

        # false value
        self.assert_to_argument([], x, False)

        # true value
        self.assert_to_argument(["-d"], x, True)

    def test_arg_enum(self):
        x = dib.ArgEnum("choice", "", enum=["one", "two", "three"])
        self.assertEqual(
            {"choice": {"type": "string", "enum": ["one", "two", "three"]}},
            x.to_schema(),
        )
        self.assert_to_argument(["--choice", "one"], x, "one")
        self.assert_schema_validate(x, "two")
        self.assert_schema_validate(x, "four", assert_failure=True)

    def test_arg_flag_repeating(self):
        x = dib.ArgFlagRepeating("log_level", "", arg="-v", max_repeat=3)
        self.assertEqual(
            {"log_level": {"type": "integer", "enum": [0, 1, 2, 3]}},
            x.to_schema(),
        )
        self.assert_to_argument([], x, 0)
        self.assert_to_argument(["-v"], x, 1)
        self.assert_to_argument(["-v", "-v"], x, 2)
        self.assert_to_argument(["-v", "-v", "-v"], x, 3)

    def test_arg_int(self):
        x = dib.ArgInt("size", "")
        self.assertEqual(
            {"size": {"type": "integer", "minimum": 1}}, x.to_schema()
        )
        self.assert_to_argument(["--size", "10"], x, 10)
        self.assert_schema_validate(x, -1, assert_failure=True)

    def test_arg_list(self):
        x = dib.ArgList("packages", "", arg="-p")
        self.assertEqual(
            {"packages": {"type": "array", "items": {"type": "string"}}},
            x.to_schema(),
        )
        self.assert_to_argument(
            ["-p", "wget,vim-enhanced"], x, ["wget", "vim-enhanced"]
        )
        self.assert_to_argument([], x, [])

    def test_arg_list_position(self):
        x = dib.ArgListPositional("elements", "")
        self.assert_to_argument(
            ["centos", "vm", "bootloader"], x, ["centos", "vm", "bootloader"]
        )

    def test_arg_enum_list(self):
        x = dib.ArgEnumList(
            "types", "", arg="-t", enum=["qcow2", "tar", "raw"]
        )
        self.assertEqual(
            {
                "types": {
                    "items": {
                        "enum": ["qcow2", "tar", "raw"],
                        "type": "string",
                    },
                    "type": "array",
                }
            },
            x.to_schema(),
        )
        self.assert_to_argument(["-t", "qcow2,raw"], x, ["qcow2", "raw"])

    def test_arg_dict_to_string(self):
        x = dib.ArgDictToString("options", "")
        self.assertEqual(
            {
                "options": {
                    "additionalProperties": {"type": "string"},
                    "type": "object",
                }
            },
            x.to_schema(),
        )
        self.assert_to_argument(
            ["--options", "foo=bar,baz=ingo"],
            x,
            {"foo": "bar", "baz": "ingo"},
        )

    def test_command_merged_env(self):
        c = dib.Command(
            "echo",
            properties=[dib.Env("environment", "")],
            entry={
                "environment": {
                    "ELEMENTS_PATH": "/path/to/elements",
                    "DIB_CLOUD_IMAGES": "/path/to/image.qcow2",
                }
            },
        )
        env = c.merged_env()
        self.assertEqual("/path/to/elements", env["ELEMENTS_PATH"])
        self.assertEqual("/path/to/image.qcow2", env["DIB_CLOUD_IMAGES"])
        self.assertIn(needle="_LIB", haystack=env)
        # this will be merged with the whole environment, so there will be
        # more than 3 values
        self.assertGreater(len(env), 3)

    def test_command(self):
        c = dib.Command(
            "echo",
            properties=[
                dib.Env("environment", ""),
                dib.Arg("the-key", "", arg="--key"),
                dib.ArgFlag("doit", "do it", arg="-d"),
                dib.ArgFlagRepeating("verbose", "", arg="-v", max_repeat=3),
                dib.ArgDictToString("options", ""),
                dib.ArgListPositional("elements", ""),
            ],
            entry={
                "environment": {
                    "ELEMENTS_PATH": "/path/to/elements",
                    "DIB_CLOUD_IMAGES": "~/image.qcow2",
                },
                "the-key": "the-value",
                "doit": True,
                "verbose": 3,
                "options": {"foo": "bar"},
                "elements": ["centos", "vm"],
            },
        )
        self.assertEqual(
            [
                "bash",
                "echo",
                "--key",
                "the-value",
                "-d",
                "-v",
                "-v",
                "-v",
                "--options",
                "foo=bar",
                "centos",
                "vm",
            ],
            c.command(),
        )
        self.assertEqual(
            "ELEMENTS_PATH=/path/to/elements "
            "DIB_CLOUD_IMAGES='~/image.qcow2' "
            "bash echo --key the-value -d -v -v -v --options foo=bar "
            "centos vm\n",
            str(c),
        )

    def test_merge_entry(self):
        # override normal attributes
        merged_entry = {
            "imagename": "image1",
            "elements": ["one", "two", "three"],
            "debug-trace": 1,
        }
        dib.merge_entry(
            merged_entry,
            {
                "imagename": "image1",
                "debug-trace": 2,
                "logfile": "image1.log",
            },
        )
        self.assertEqual(
            {
                "imagename": "image1",
                "elements": ["one", "two", "three"],
                "debug-trace": 2,
                "logfile": "image1.log",
            },
            merged_entry,
        )

        # append list attributes, update dict attributes
        merged_entry = {
            "imagename": "image1",
            "elements": ["one", "two", "three"],
            "environment": {
                "DIB_ONE": "1",
                "DIB_TWO": "2",
            },
        }
        dib.merge_entry(
            merged_entry,
            {
                "imagename": "image1",
                "elements": ["four", "five"],
                "environment": {
                    "DIB_TWO": "two",
                    "DIB_THREE": "three",
                },
            },
        )
        self.assertEqual(
            {
                "imagename": "image1",
                "elements": ["one", "two", "three", "four", "five"],
                "environment": {
                    "DIB_ONE": "1",
                    "DIB_TWO": "two",
                    "DIB_THREE": "three",
                },
            },
            merged_entry,
        )

    @mock.patch("diskimage_builder.paths.get_path")
    def test_build_commands_simple(self, mock_get_path):
        mock_get_path.return_value = "/lib"
        commands = dib.build_commands(
            [
                {
                    "imagename": "centos-minimal",
                    "elements": ["centos", "vm"],
                },
                {
                    "imagename": "ironic-python-agent",
                    "ramdisk": True,
                    "elements": [
                        "ironic-python-agent-ramdisk",
                        "extra-hardware",
                    ],
                },
            ]
        )

        self.assertEqual(
            [
                "bash",
                "/lib/disk-image-create",
                "-o",
                "centos-minimal",
                "centos",
                "vm",
            ],
            commands[0].command(),
        )
        self.assertEqual(
            [
                "bash",
                "/lib/ramdisk-image-create",
                "-o",
                "ironic-python-agent",
                "ironic-python-agent-ramdisk",
                "extra-hardware",
            ],
            commands[1].command(),
        )

    @mock.patch("diskimage_builder.paths.get_path")
    def test_build_commands_merged(self, mock_get_path):
        mock_get_path.return_value = "/lib"
        commands = dib.build_commands(
            [
                {  # base definition
                    "imagename": "centos-minimal",
                    "elements": ["centos", "vm"],
                    "environment": {"foo": "bar", "zip": "zap"},
                },
                {  # merge with previous when no imagename
                    "elements": ["devuser"],
                    "logfile": "centos-minimal.log",
                },
                {  # merge when same imagename
                    "imagename": "centos-minimal",
                    "environment": {"foo": "baz", "one": "two"},
                },
            ]
        )

        self.assertEqual(1, len(commands))
        self.assertEqual(
            [
                "bash",
                "/lib/disk-image-create",
                "-o",
                "centos-minimal",
                "--logfile",
                "centos-minimal.log",
                "centos",
                "vm",
                "devuser",
            ],
            commands[0].command(),
        )

    @mock.patch("diskimage_builder.paths.get_path")
    def test_build_commands_all_arguments(self, mock_get_path):
        mock_get_path.return_value = "/lib"
        commands = dib.build_commands(
            [
                {
                    "arch": "amd64",
                    "imagename": "everyoption",
                    "types": ["qcow2"],
                    "debug-trace": 2,
                    "uncompressed": True,
                    "clear": True,
                    "logfile": "./logfile.log",
                    "checksum": True,
                    "image-size": 40,
                    "image-extra-size": 1,
                    "image-cache": "~/.cache/dib",
                    "max-online-resize": 1000,
                    "min-tmpfs": 7,
                    "mkfs-journal-size": 1,
                    "mkfs-options": "-D",
                    "no-tmpfs": True,
                    "offline": True,
                    "qemu-img-options": {"size": "10"},
                    "ramdisk-element": "dracut-ramdisk",
                    "install-type": "package",
                    "root-label": "root",
                    "docker-target": "everyoption:latest",
                    "packages": ["wget", "tmux"],
                    "skip-base": True,
                    "elements": ["centos", "vm"],
                }
            ]
        )

        self.assertEqual(
            [
                "bash",
                "/lib/disk-image-create",
                "-o",
                "everyoption",
                "-a",
                "amd64",
                "-t",
                "qcow2",
                "-x",
                "-x",
                "-u",
                "-c",
                "--logfile",
                "./logfile.log",
                "--checksum",
                "--image-size",
                "40",
                "--image-extra-size",
                "1",
                "--image-cache",
                "~/.cache/dib",
                "--max-online-resize",
                "1000",
                "--min-tmpfs",
                "7",
                "--mkfs-journal-size",
                "1",
                "--mkfs-options",
                "-D",
                "--no-tmpfs",
                "--offline",
                "--qemu-img-options",
                "size=10",
                "--root-label",
                "root",
                "--ramdisk-element",
                "dracut-ramdisk",
                "--install-type",
                "package",
                "--docker-target",
                "everyoption:latest",
                "-p",
                "wget,tmux",
                "-n",
                "centos",
                "vm",
            ],
            commands[0].command(),
        )

    def write_image_definition(self):
        image_def = [
            {
                "imagename": "centos-minimal",
                "elements": ["centos", "vm"],
            },
            {
                "imagename": "ironic-python-agent",
                "ramdisk": True,
                "elements": [
                    "ironic-python-agent-ramdisk",
                    "extra-hardware",
                ],
            },
        ]
        with tempfile.NamedTemporaryFile(delete=False) as deffile:
            self.addCleanup(os.remove, deffile.name)
            self.filelist = [deffile.name]
            with open(deffile.name, "w") as f:
                f.write(yaml.dump(image_def))
        return deffile.name

    @mock.patch("diskimage_builder.paths.get_path")
    @mock.patch("diskimage_builder.diskimage_builder.get_args")
    @mock.patch("subprocess.Popen")
    def test_main_dry_run(self, mock_popen, mock_get_args, mock_get_path):
        mock_get_path.return_value = "/lib"
        mock_get_args.return_value = mock.Mock(
            dry_run=True, files=[self.write_image_definition()]
        )
        dib.main()
        mock_popen.assert_not_called()

    @mock.patch("diskimage_builder.paths.get_path")
    @mock.patch("diskimage_builder.diskimage_builder.get_args")
    @mock.patch("subprocess.Popen")
    def test_main(self, mock_popen, mock_get_args, mock_get_path):
        mock_get_path.return_value = "/lib"
        mock_get_args.return_value = mock.Mock(
            dry_run=False,
            files=[self.write_image_definition()],
            stop_on_failure=False,
        )

        process = mock.Mock()
        process.returncode = 0
        mock_popen.return_value = process

        dib.main()
        self.assertEqual(2, mock_popen.call_count)
        mock_popen.assert_has_calls(
            [
                mock.call(
                    [
                        "bash",
                        "/lib/disk-image-create",
                        "-o",
                        "centos-minimal",
                        "centos",
                        "vm",
                    ],
                    env=mock.ANY,
                ),
                mock.call(
                    [
                        "bash",
                        "/lib/ramdisk-image-create",
                        "-o",
                        "ironic-python-agent",
                        "ironic-python-agent-ramdisk",
                        "extra-hardware",
                    ],
                    env=mock.ANY,
                ),
            ],
            any_order=True,
        )

    @mock.patch("diskimage_builder.paths.get_path")
    @mock.patch("diskimage_builder.diskimage_builder.get_args")
    @mock.patch("subprocess.Popen")
    def test_main_stop_on_failure(
        self, mock_popen, mock_get_args, mock_get_path
    ):
        mock_get_path.return_value = "/lib"
        mock_get_args.return_value = mock.Mock(
            dry_run=False,
            files=[self.write_image_definition()],
            stop_on_failure=True,
        )

        process = mock.Mock()
        process.returncode = -1
        mock_popen.return_value = process

        e = self.assertRaises(subprocess.CalledProcessError, dib.main)
        self.assertEqual(1, mock_popen.call_count)
        self.assertEqual(-1, e.returncode)

    @mock.patch("diskimage_builder.paths.get_path")
    @mock.patch("diskimage_builder.diskimage_builder.get_args")
    @mock.patch("subprocess.Popen")
    def test_main_continue_on_failure(
        self, mock_popen, mock_get_args, mock_get_path
    ):
        mock_get_path.return_value = "/lib"
        mock_get_args.return_value = mock.Mock(
            dry_run=False,
            files=[self.write_image_definition()],
            stop_on_failure=False,
        )

        process = mock.Mock()
        process.returncode.side_effect = -1
        mock_popen.return_value = process

        self.assertRaises(subprocess.CalledProcessError, dib.main)
        self.assertEqual(2, mock_popen.call_count)
