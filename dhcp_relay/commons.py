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

# import stdlib
from threading import Lock

# third party libs
from timeout_decorator import timeout

# import local modules
from dhcp_relay.defaults import DHCPDefaults

_MAX_WAIT_TIME = DHCPDefaults.MAX_WAIT


class DHCPCommons:

    # common objects across listener instances
    XID_MAC = {}
    SUBS_UP = {}
    MAC_IP = {}
    LAST_PKT_SENT = 0

    _xid_mac_lock = Lock()
    _subs_up_lock = Lock()
    _mac_ip_lock = Lock()
    _last_pkt_sent_lock = Lock()

    def __init__(self, max_wait):
        _MAX_WAIT_TIME = max_wait

    @timeout(_MAX_WAIT_TIME)
    def _acquire_wait(self, locker):
        while not locker.acquire(False):
            pass

    def _acquire_and_push(self, key, value, attr, locker):
        self._acquire_wait(locker)
        getattr(self, attr)[key] = value
        self.locker.release()

    def _acquire_and_pop(self, key, attr, locker, default=''):
        self._acquire_wait(locker)
        val = getattr(self, attr).pop(key, default)
        self.locker.release()
        return val

    def xid_mac(self, key, value):
        self._acquire_and_push(key, value, 'XID_MAC', _xid_mac_lock)

    def xid_mac_pop(self, key):
        return self._acquire_and_pop(key, 'XID_MAC', _xid_mac_lock)

    def subs_up(self, key, value):
        self._acquire_and_push(key, value, 'SUBS_UP', _subs_up_lock)

    def subs_up_pop(self, key):
        return self._acquire_and_pop(key, 'SUBS_UP', _subs_up_lock)

    def mac_ip(self, key, value):
        self._acquire_and_push(key, value, 'MAC_IP', _mac_ip_lock)

    def mac_ip_pop(self, key):
        return self._acquire_and_pop(key, 'MAC_IP', _mac_ip_lock)

    @property
    def last_pkt_sent(self):
        return self.LAST_PKT_SENT

    @last_pkt_sent.setter
    def last_pkt_sent(self, value):
        self._acquire_wait(_last_pkt_sent_lock)
        self.LAST_PKT_SENT = value
        self._last_pkt_sent_lock.release()
