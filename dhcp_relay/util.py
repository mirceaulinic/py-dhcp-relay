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

import string

from netaddr import IPAddress
from netaddr.core import AddrFormatError


ALL_CHARS = ''.join(chr(c) for c in range(256))
DEL_CHARS = set(ALL_CHARS) - set(string.hexdigits)


def check_mac_address(mac_address):

    mac_address = mac_address.translate(''.join(ALL_CHARS), ''.join(DEL_CHARS))
    if len(mac_address) == 12:  # MAC Address has always 12 HEX chars
        return True

    return False


def check_xid(xid):

    if not len(xid) == 4:
        return False
    if not(0 <= xid[0] <= 255 and 0 <= xid[1] <= 255 and 0 <= xid[2] <= 255 and 0 <= xid[3] <= 255):
        return False

    return True


def check_ip_address(ip_address):

    try:
        IPAddress(ip_address)
    except AddrFormatError:
        return False
    return True
