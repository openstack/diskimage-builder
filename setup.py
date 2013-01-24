#!/usr/bin/python
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import setuptools

with open("README.md", 'rt') as readme:
    readme_text = readme.read()

setuptools.setup(
    name='diskimage_builder',
    version='0.0.1',
    description="""Build Disk Images for use on OpenStack Nova""",
    long_description = readme_text,
    license='Apache License (2.0)',
    author='HP Cloud Services',
    author_email='nobody@hp.com',
    url='https://github.com/stackforge/diskimage-builder',
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Environment :: Console',
    ],
    scripts=['bin/element-info'],
    py_modules=[])
