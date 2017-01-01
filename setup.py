# -*- coding: utf-8 -*-
# Copyright 2016, 2017 Mircea Ulinic. All rights reserved.
#
# The contents of this file are licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

from setuptools import setup, find_packages
from pip.req import parse_requirements
import uuid

install_reqs = parse_requirements('requirements.txt', session=uuid.uuid1())

reqs = [str(ir.req) for ir in install_reqs]

__version__ = '0.0.1'

setup(
    name = 'dhcp-relay',
    version  = __version__,
    packages = find_packages(),
    platforms = 'any',
    install_requires = reqs,
    include_package_data = True,
    description = 'Python library to act as a DHCP relay',
    author = 'Mircea Ulinic',
    author_email = 'mircea.ulinic@cloudflare.com',
    url = 'https://github.com/mirceaulinic/py-dhcp-relay',  # use the URL to the github repo
    download_url = 'https://github.com/mirceaulinic/py-dhcp-relay/tarball/%s' % __version__,
    keywords = ['network', 'DHCP', 'relay'],
    license = 'GPL 3.0',
    scripts = ['dhcp_relay/bin/dhcp-relay'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'Intended Audience :: Telecommunications Industry',
        'Operating System :: OS Independent',
        'Topic :: System :: Networking',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries',
        'Topic :: Scientific/Engineering',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
      ]
)
