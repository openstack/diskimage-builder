#
# Copyright 2017 Andreas Florath (andreas@florath.net)
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
#
# Scan the element directory, looks for element  dependencies and
# writes them out when the directive
#   .. element_deps::
# is used.
# This was developed only for internal use and must be called
# from the source top directory.

from diskimage_builder.element_dependencies import _find_all_elements
from diskimage_builder.paths import get_path

from docutils.parsers.rst import Directive
import os

all_elements = _find_all_elements(get_path("elements"))


def make_dep_list(title, deps):
    lines = []
    lines.append(title)
    lines.append("+" * len(title))
    for dep in deps:
        lines.append("* :doc:`../%s/README`" % dep)
    lines.append('')  # careful to end with a blank line
    return lines


class ElementDepsDirective(Directive):

    # this enables content in the directive
    has_content = True

    def run(self):
        source = self.state_machine.input_lines.source(
            self.lineno - self.state_machine.input_offset - 1)
        # Extract the element from the source attribute of the document
        element_name = os.path.basename(os.path.dirname(
            self.state_machine.document.attributes['source']))

        lines = ["Element Dependencies",
                 "--------------------"]

        # This should not fail -- sphinx would be finding an element
        # that dib doesn't know about?
        element = all_elements[element_name]
        if element.depends:
            lines.extend(make_dep_list("Uses", element.depends))
        if element.r_depends:
            lines.extend(make_dep_list("Used by", element.r_depends))

        self.state_machine.insert_input(lines, source)

        return []


def setup(app):
    app.add_directive('element_deps', ElementDepsDirective)
