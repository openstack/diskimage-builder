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

SIZE_SPECS = [
    ["TiB", 1024**4],
    ["GiB", 1024**3],
    ["MiB", 1024**2],
    ["KiB", 1024**1],
    ["TB", 1000**4],
    ["GB", 1000**3],
    ["MB", 1000**2],
    ["KB", 1000**1],
    ["T", 1000**4],
    ["G", 1000**3],
    ["M", 1000**2],
    ["K", 1000**1],
    ["B", 1],
    ["", 1],   # No unit -> size is given in bytes
]


def _split_size_spec(size_spec):
    for spec_key, spec_value in SIZE_SPECS:
        if len(spec_key) == 0:
            return size_spec, spec_key
        if size_spec.endswith(spec_key):
            return size_spec[:-len(spec_key)], spec_key
    raise RuntimeError("size_spec [%s] not known" % size_spec)


def _get_unit_factor(unit_str):
    for spec_key, spec_value in SIZE_SPECS:
        if unit_str == spec_key:
            return spec_value
    raise RuntimeError("unit_str [%s] not known" % unit_str)


def parse_abs_size_spec(size_spec):
    size_cnt_str, size_unit_str = _split_size_spec(size_spec)
    unit_factor = _get_unit_factor(size_unit_str)
    return int(unit_factor * (
        float(size_cnt_str) if len(size_cnt_str) > 0 else 1))


def convert_to_utf8(jdata):
    """Convert to UTF8.

    The json parser returns unicode strings. Because in
    some python implementations unicode strings are not
    compatible with utf8 strings - especially when using
    as keys in dictionaries - this function recursively
    converts the json data.
    """
    if isinstance(jdata, unicode):
        return jdata.encode('utf-8')
    elif isinstance(jdata, dict):
        return {convert_to_utf8(key): convert_to_utf8(value)
                for key, value in jdata.iteritems()}
    elif isinstance(jdata, list):
        return [convert_to_utf8(je) for je in jdata]
    else:
        return jdata
