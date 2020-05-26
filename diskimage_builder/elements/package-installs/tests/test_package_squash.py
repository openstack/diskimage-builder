# Copyright 2018 Red Hat, Inc.
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
import collections
import functools
import imp
import mock
import os

from oslotest import base
from testtools.matchers import Mismatch

installs_squash_src = (os.path.dirname(os.path.realpath(__file__)) +
                       '/../bin/package-installs-squash')
installs_squash = imp.load_source('installs_squash', installs_squash_src)


class IsMatchingInstallList(object):

    def __init__(self, expected):
        self.expected = expected

    def match(self, actual):
        for phase, ops in self.expected.items():
            if phase not in actual:
                # missing the phase
                return Mismatch(
                    "Phase %d does not exist in %s" % (phase, actual))
            for op, pkgs in ops.items():
                if op not in actual[phase]:
                    # missing op (install/uninstall)
                    return Mismatch(
                        "Operation %s does not exist in %s" % (op, ops))
                # on py2 these can be out of order, we just want a match
                expected_phase_ops = sorted(self.expected[phase][op])
                actual_phase_ops = sorted(actual[phase][op])
                if expected_phase_ops != actual_phase_ops:
                    return Mismatch(
                        "Operation list %s does not match expected  %s" %
                        (actual[phase][op], self.expected[phase][op]))


class TestPackageInstall(base.BaseTestCase):
    def setUp(self):
        super(TestPackageInstall, self).setUp()
        self.final_dict = collections.defaultdict(
            functools.partial(collections.defaultdict, list))

    def test_simple(self):
        '''Test a basic package install'''
        objs = {
            'test_package': ''
        }

        result = installs_squash.collect_data(
            self.final_dict, objs, 'test_element')

        expected = {
            'install.d': {
                'install': [('test_package', 'test_element')]
            }
        }

        self.assertThat(result, IsMatchingInstallList(expected))

    @mock.patch.object(os, 'environ', dict(ARCH='arm64', **os.environ))
    def test_arch(self):
        '''Exercise the arch and not-arch flags'''
        objs = {
            'test_package': '',
            'test_arm64_package': {
                'arch': 'arm64'
            },
            'do_not_install': {
                'not-arch': 'arm64'
            }
        }

        result = installs_squash.collect_data(
            self.final_dict, objs, 'test_element')

        expected = {
            'install.d': {
                'install': [('test_package', 'test_element'),
                            ('test_arm64_package', 'test_element')]
            }
        }

        self.assertThat(result, IsMatchingInstallList(expected))

    kernel_objs = {
        'linux-image-generic': [
            {
                'not-arch': 'arm64',
                'when': 'DIB_UBUNTU_KERNEL = linux-image-generic',
            },
            {
                'arch': 'arm64',
                'when': (
                    'DIB_RELEASE != xenial',
                    'DIB_UBUNTU_KERNEL = linux-image-generic',
                )
            },
        ],
        'linux-generic-hwe-16.04': {
            'arch': 'arm64',
            'when': (
                'DIB_RELEASE = xenial',
                'DIB_UBUNTU_KERNEL = linux-image-generic',
            )
        },
    }

    def _test_kernel_objs_match(self, arch, release, expected):
        with mock.patch.object(os, 'environ',
                               dict(ARCH=arch,
                                    DIB_UBUNTU_KERNEL='linux-image-generic',
                                    DIB_RELEASE=release,
                                    **os.environ)):
            result = installs_squash.collect_data(
                self.final_dict, self.kernel_objs, 'test_element')

        expected = {
            'install.d': {
                'install': [(expected, 'test_element')]
            }
        }
        self.assertThat(result, IsMatchingInstallList(expected))

    def test_param_list_x86(self):
        self._test_kernel_objs_match('x86_64', 'focal', 'linux-image-generic')

    def test_param_list_arm64_xenial(self):
        self._test_kernel_objs_match('arm64', 'xenial',
                                     'linux-generic-hwe-16.04')

    def test_param_list_arm64_focal(self):
        self._test_kernel_objs_match('arm64', 'focal', 'linux-image-generic')

    @mock.patch.object(os, 'environ', dict(DIB_FEATURE='1', **os.environ))
    def test_skip_when(self):
        '''Exercise the when flag'''
        objs = {
            'skipped_package': {
                'when': 'DIB_FEATURE=0'
            },
            'not_skipped_package': {
                'when': 'DIB_FEATURE=1'
            },
            'not_equal_package': {
                'when': 'DIB_FEATURE!=0'
            },
            'not_equal_skipped_package': {
                'when': 'DIB_FEATURE!=1'
            },
        }

        result = installs_squash.collect_data(
            self.final_dict, objs, 'test_element')

        expected = {
            'install.d': {
                'install': [('not_skipped_package', 'test_element'),
                            ('not_equal_package', 'test_element')]
            }
        }

        self.assertThat(result, IsMatchingInstallList(expected))

    def test_skip_no_var(self):
        '''Exercise the skip_when missing variable failure case'''
        objs = {
            'package': {
                'when': 'MISSING_VAR=1'
            },
        }

        self.assertRaises(RuntimeError, installs_squash.collect_data,
                          self.final_dict, objs, 'test_element')

    @mock.patch.object(os, 'environ',
                       dict(
                           DIB_A_FEATURE='1',
                           DIB_B_FEATURE='1',
                           DIB_C_FEATURE='1',
                           **os.environ))
    def test_skip_when_list(self):
        '''Exercise the when flag with lists'''
        objs = {
            'not_skipped_package': {
                'when': [
                    'DIB_A_FEATURE=1',
                    'DIB_B_FEATURE=1',
                    'DIB_C_FEATURE=1'
                ]
            },
            'skipped_package': {
                'when': [
                    'DIB_A_FEATURE=1',
                    'DIB_B_FEATURE=0',
                    'DIB_C_FEATURE=1',
                ]
            },
        }

        result = installs_squash.collect_data(
            self.final_dict, objs, 'test_element')

        expected = {
            'install.d': {
                'install': [('not_skipped_package', 'test_element')]
            }
        }

        self.assertThat(result, IsMatchingInstallList(expected))
