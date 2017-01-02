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

# std lib
import os
import time
import random
import hashlib

# third party libs
from timeout_decorator import timeout

# local modules
import dhcp_relay.exceptions
from dhcp_relay.commons import DHCPCommons
from dhcp_relay.defaults import DHCPDefaults
from dhcp_relay.globals import DHCPGlobals
from dhcp_relay.listener import DHCPListener
from dhcp_relay.pkt_crafter import DHCPPktCrafter

_MAX_WAIT_TIME = DHCPDefaults.MAX_WAIT


class DHCPRelay(DHCPCommons, DHCPGlobals):

    def __init__(self,
                 config_file=None,
                 server_ip=None,
                 server_id=None,
                 server_port=None,
                 client_ip=None,
                 client_port=None,
                 lease_time=None,
                 listener_threads=None,
                 max_wait=None,
                 log_level=None,
                 log_file=None,
                 log_full=None,
                 log_date_format=None,
                 daemon=None,
                 multiprocessing=None):
        DHCPGlobals.__init__(self,
                             config_file=config_file,
                             server_ip=server_ip,
                             server_id=server_id,
                             server_port=server_port,
                             client_ip=client_ip,
                             client_port=client_port,
                             lease_time=lease_time,
                             listener_threads=listener_threads,
                             max_wait=max_wait,
                             log_level=log_level,
                             log_file=log_file,
                             log_full=log_full,
                             log_date_format=log_date_format,
                             daemon=daemon,
                             multiprocessing=multiprocessing)
        _MAX_WAIT_TIME = self.MAX_WAIT
        self._pkt_crafter = DHCPPktCrafter(self, logger)
        self._logger = logger

    def connect():
        self._pkt_crafter.connect()
        _listeners = list()
        for _ in range(DHCPGlobals.LISTENERS):  # start as many listeners as needed
            _listener = DHCPListener(self._pkt_crafter, self._logger)
            _listeners.append(_listener)
        for _listener in _listeners:
            _listener.start()

    @staticmethod
    def _xid():
        _xid = [
            random.randrange(255),
            random.randrange(255),
            random.randrange(255),
            random.randrange(255),
        ] # random transaction ID
        return _xid

    @staticmethod
    def _rid():
        return hashlib.md5(str(time.time())).hexdigest()

    def send_discover(self, mac, ip=None):
        _xid = self._xid()
        _rid = self._rid()  # Unique Request ID
        _xid_str = '.'.join([str(xid_e) for xid_e in xid])
        self.xid_mac_map[_xid_str] = mac
        self.subs_up[mac] = False
        if not ip:
            ip = self.DUMMY_IP_ADDRESS
            # if no specific IP Address is requested,
            # will try to request something dummy
        return self._pkt_crafter.send_discover(_rid, _xid, mac, ip)
        # sends DHCP Discover Packet

    @timeout(_MAX_WAIT_TIME)
    def bring_subscriber_up(self, mac, ip=None):
        if not self.send_discover(mac, ip):
            return False
        start_time = time.time()
        while (not self.subs_up.get(mac, '')):
            continue  # wait till subs comes up
        self.subs_up.pop(mac, '')
        return self.mac_ip_map.pop(mac, '')  # returns the assigned IP Address

    def bring_subscribers_list_up(self, mac_list):
        for mac in mac_list:
            self.send_discover(mac)
        return True

    def send_release(self, mac):
        _xid = self._xid()
        _rid = self._rid()
        self._pkt_crafter.send_release(_rid, _xid, mac)

    def bring_subscriber_down(self, mac):
        self.send_release(mac)
        return True
