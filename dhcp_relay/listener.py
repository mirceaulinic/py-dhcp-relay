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
import logging
from threading import Thread

# local modules
from dhcp_relay.globals import DHCPGlobals

log = logging.getLogger(__name__)


class DHCPListener(DHCPGlobals, Thread):

    def __init__(self,
                 relay,
                 pkt_crafter):
        Thread.__init__(self)
        self._relay = relay
        self._pkt_crafter = pkt_crafter
        log.addHandler(self._relay.LOGGING_HANDLER)

    def run(self):
        while True:
            received_packet = self._pkt_crafter.GetNextDhcpPacket()
            if received_packet is not None:
                xid = received_packet.GetOption("xid")
                xid_str = '.'.join([str(xid_e) for xid_e in xid])
                mac = self._relay.XID_MAC.get(xid_str)
                pkt_type = ''
                if received_packet.IsDhcpOfferPacket() and mac:
                    pkt_type = 'DHCPOFFER'
                    assigned_ip_address = received_packet.GetOption("yiaddr")
                    lease_time = received_packet.GetOption("ip_address_lease_time")
                    self._relay.mac_ip(mac, assigned_ip_address)
                    self._pkt_crafter.send_request(
                        xid,
                        mac,
                        assigned_ip_address,
                        lease_time
                    )
                elif received_packet.IsDhcpAckPacket():
                    pkt_type = 'DHCPACK'
                    self._relay.xid_mac_pop(xid_str)
                    if mac:
                        self._relay.subs_up(mac, True)
                if self._relay.LOGGING_ENABLED:
                    log.info('Received {pkt_type} message from AC, for XID: '
                             '{xid}, corresponding for MAC address: {mac}.'\
                                .format(xid=str(xid),
                                        mac=str(mac),
                                        pkt_type=pkt_type))
                    if self._relay.DETAILED_LOG:
                        log.debug('Packet structure')
                        log.debug(received_packet.str())
