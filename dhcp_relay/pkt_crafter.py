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
import time
import logging

# third party libs
import pydhcplib
from pydhcplib.dhcp_packet import *
from pydhcplib.dhcp_network import *

# import local modules
import dhcp_relay.util
import dhcp_relay.exceptions
from dhcp_relay.globals import DHCPGlobals

log = logging.getLogger(__name__)


class DHCPPktCrafter(DhcpClient):

    PKT_CRAFTER_UP = False

    def __init__(self,
                 relay):
        self._relay = relay
        log.addHandler(self._relay.LOGGING_HANDLER)

    def connect(self):
        DhcpClient.__init__(
            self,
            self._relay.CLIENT_IP,
            self._relay.SERVER_PORT,
            self._relay.SERVER_PORT
        )
        self._client_ip_address_pydhcplib = pydhcplib.type_ipv4.ipv4(self._relay.CLIENT_IP).list()
        self._server_identifier_pydhcplib = pydhcplib.type_ipv4.ipv4(self._relay.SERVER_ID).list()
        # to not compute it when sending every packet
        try:
            self.BindToAddress()
        except pydhcplib.DhcpNetwork.BindToAddress as bta:
            log.critical(bta.message)
            base_msg = 'Unable to bind to {cip}:{cport}'.format(
                cip=self._relay.CLIENT_IP,
                cport=self._relay.CLIENT_PORT)
            log.critical(base_msg)
            log.critical('Please specify the right details under the config file: {cfile}'.format(
                cfile=self._relay.CONFIG_FILE))
            raise dhcp_relay.exceptions.BindError(base_msg)
        self.PKT_CRAFTER_UP = True

    def _build_basic_pkt(self,
                         pkt_type,
                         xid,
                         mac=None):
        if not self.PKT_CRAFTER_UP:
            log.critical('Cannot build DHCP packets. Is the relay UP?')
            return
        if pkt_type not in self._relay.DHCPLIB_CONSTANTS.keys():
            raise dhcp_relay.exceptions.PktTypeError(
                "Invalid DHCP packet type: {pkt_type}. Choose between: {pkt_type_list}.".format(
                    pkt_type=pkt_type,
                    pkt_type_list=', '.join(self._relay.DHCPLIB_CONSTANTS.keys())
                )
            )
        packet = DhcpPacket()
        packet.SetOption("op", [self._relay.DHCPLIB_CONSTANTS.get(pkt_type, {}).get('op', 1)])  # REQUEST
        # See http://www.iana.org/assignments/arp-parameters/arp-parameters.xhtml
        # htype 29 : IP and ARP over ISO 7816-3
        packet.SetOption("htype", [29])  #
        packet.SetOption("hlen", [6])  # Hardware address length
        packet.SetOption("hops", [self.MAX_HOPS])  # Number of hops
        packet.SetOption("giaddr", self._client_ip_address_pydhcplib)
        packet.SetOption("xid", xid)  # Transaction ID
        packet.SetOption("dhcp_message_type",
                         [self._relay.DHCPLIB_CONSTANTS.get(pkt_type).get('dhcp_message_type')])
        packet.SetOption("server_identifier", self._server_identifier_pydhcplib)
        if mac:
            packet.SetOption("chaddr", pydhcplib.type_hw_addr.hwmac(mac).list() + [0] * 10)  # Client hardware address
            packet.SetOption("host_name", pydhcplib.type_strlist.strlist(mac).list())
            packet.SetOption("client_identifier", pydhcplib.type_strlist.strlist(mac).list())

        return packet

    def _send_packet(self, pkt):
        if not self.PKT_CRAFTER_UP:
            log.critical('Unable to send DHCP packets. Is the relay UP?')
            return
        if self._relay.DDOS_LIMIT:
            if (time.time() - self._relay.last_pkt_sent) < self._relay.PKT_SPLAY:
                time.sleep((self._relay.last_pkt_sent + self._relay.PKT_SPLAY) - time.time())
        send_result = self.SendDhcpPacketTo(
            pkt,
            self._relay.SERVER_IP,
            self._relay.SERVER_PORT
        )
        self._relay.last_pkt_sent = time.time()
        return send_result

    def _basic_sender_with_rid(self,
                               pkt_type,
                               rid,
                               xid,
                               mac,
                               ip=None):
        if not self.PKT_CRAFTER_UP:
            log.critical('Unable to send DHCP packets. Is the relay UP?')
            return
        if self._relay.LOGGING_ENABLED:
            log.info('Received request #{rid} to send {pkt_type} packet for MAC '
                     'Address: {mac}, using XID: {xid}'.format(rid=rid,
                                                               mac=str(mac),
                                                               xid=str(xid),
                                                               pkt_type=pkt_type))
        if not dhcp_relay.util.check_xid(xid):
            if self._relay.LOGGING_ENABLED:
                log.error('Invalid XID ({xid}) for request #{rid}'.format(
                    rid=rid,
                    xid=str(xid)))
            return False
        if not dhcp_relay.util.check_mac_address(mac):
            if self._relay.LOGGING_ENABLED:
                log.error('Invalid MAC Address ({mac}) for request #{rid}'.format(
                    rid=rid,
                    mac=str(mac)))
            return False
        try:
            packet = self._build_basic_pkt(pkt_type=pkt_type, xid=xid, mac=mac)
            if pkt_type == 'DHCPDISCOVER' and dhcp_relay.util.check_ip_address(ip):
                packet.SetOption("request_ip_address", pydhcplib.type_ipv4.ipv4(ip).list()) # Requested IP address
            self._send_packet(packet)
        except Exception as e:
            if self._relay.LOGGING_ENABLED:
                log.error('Cannot send {pkt_type} for request #{rid}. '
                          'Cause: {err}'.format(rid=rid,
                                                err=str(e),
                                                pkt_type=pkt_type))
            return False
        if self._relay.LOGGING_ENABLED:
            log.info('{pkt_type} sent for request #{rid}.'.format(
                rid=rid,
                pkt_type=pkt_type))
            if self._relay.DETAILED_LOG:
                log.info('Packet structure')
                log.info(packet.str())
        return True

    def send_discover(self,
                      rid,
                      xid,
                      mac,
                      ip=None):
        return self._basic_sender_with_rid('DHCPDISCOVER', rid, xid, mac, ip)

    def send_request(self,
                     xid,
                     mac,
                     ip,
                     lease_time):
        if self._relay.LOGGING_ENABLED:
            log.info('Received request to send DHCPREQUEST packet for MAC '
                     'Address: {mac}, using XID: {xid}'.format(mac=str(mac),
                                                               xid=str(xid)))
        if not dhcp_relay.util.check_xid(xid):
            if self._relay.LOGGING_ENABLED:
                log.error('Invalid XID ({xid})'.format(xid=str(xid)))
            return False
        if not dhcp_relay.util.check_mac_address(mac):
            if self._relay.LOGGING_ENABLED:
                log.error('Invalid MAC Address ({mac}) for XID {xid}'.format(
                    xid=xid,
                    mac=str(mac)))
            return False
        if not dhcp_relay.util.check_ip_address(ip):
            if self._relay.LOGGING_ENABLED:
                log.error('Invalid IP Address ({ip}) for XID {xid}'.format(
                    xid=xid,
                    ip=str(ip)))
            return False
        try:
            packet = self._build_basic_pkt(pkt_type='DHCPREQUEST', xid=xid, mac=mac)
            packet.SetOption("request_ip_address", ip)
            packet.SetOption("ip_address_lease_time", lease_time)
            self._send_packet(packet)
        except Exception as e:
            if self._relay.LOGGING_ENABLED:
                log.error('Cannot send DHCPREQUEST for XID {xid}. Cause: {err}'.format(
                    err=str(e),
                    xid=str(xid)))
            return False
        if self._relay.LOGGING_ENABLED:
            log.info('DHCPREQUEST sent for XID: {xid}.'.format(xid=str(xid)))
            if self._relay.DETAILED_LOG:
                log.info('Packet structure:')
                log.info(packet.str())
        return True

    def send_release(self,
                     rid,
                     xid,
                     mac):
        return self._basic_sender_with_rid('DHCPRELEASE', rid, xid, mac)
