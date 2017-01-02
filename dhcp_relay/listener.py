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

from threading import Thread

# local modules
from dhcp_relay.globals import DHCPGlobals


class DHCPListener(DHCPGlobals, Thread):

    def __init__(self,
                 pkt_crafter,
                 logger=None):

        Thread.__init__(self)

        self._pkt_crafter = pkt_crafter
        self._logger = logger


    def run(self):
        while True:
            received_packet = self._pkt_crafter.GetNextDhcpPacket()
            if received_packet is not None:
                xid = received_packet.GetOption("xid")
                xid_str = '.'.join([str(xid_e) for xid_e in xid])
                mac = self._pkt_crafter.xid_mac_map.get(xid_str)
                pkt_type = ''
                if received_packet.IsDhcpOfferPacket() and mac:
                    pkt_type = 'DHCPOFFER'
                    assigned_ip_address = received_packet.GetOption("yiaddr")
                    lease_time = received_packet.GetOption("ip_address_lease_time")
                    self._pkt_crafter.mac_ip_map[mac] = assigned_ip_address
                    self._pkt_crafter.send_request(
                        xid,
                        mac,
                        assigned_ip_address,
                        lease_time
                    )
                elif received_packet.IsDhcpAckPacket():
                    pkt_type = 'DHCPACK'
                    self._pkt_crafter.xid_mac_map.pop(xid_str, '')
                    if mac:
                        self._pkt_crafter.subs_up[mac] = True
                if self._logger is not None and self.LOGGING_ENABLED:
                    log_message = 'Received {pkt_type} message from AC, for XID: {xid}, corresponding for MAC address: {mac}.'.format(
                        xid=str(xid),
                        mac=str(mac),
                        pkt_type=pkt_type
                    )
                    if self.DETAILED_LOG:
                        log_message += '\nPacket structure:\n{pkt}'.format(
                            pkt=received_packet.str()
                        )
                    self._logger.info(log_message)
