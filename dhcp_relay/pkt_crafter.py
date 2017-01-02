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

# stdlib
import time

# third party libs
import pydhcplib

from pydhcplib.dhcp_packet import *
from pydhcplib.dhcp_network import *

# local modules
import dhcp_relay.util
import dhcp_relay.exceptions

from dhcp_relay.globals import DHCPGlobals
from dhcp_relay.commons import DHCPCommons


class DHCPPktCrafter(DhcpClient):

    def __init__(self,
                 relay,
                 logger=None):
        self._relay = relay
        self._logger = logger

    def connect():
        DhcpClient.__init__(
            self,
            self.CLIENT_IP,
            self.SERVER_PORT,
            self.SERVER_PORT
        )
        self._client_ip_address_pydhcplib = pydhcplib.type_ipv4.ipv4(self.CLIENT_IP).list()
        self._server_identifier_pydhcplib = pydhcplib.type_ipv4.ipv4(self.SERVER_ID).list()
        # to not compute it when sending every packet
        self.BindToAddress()

    def _build_basic_pkt(self,
                         pkt_type,
                         xid,
                         mac=None):
        if pkt_type not in self.DHCPLIB_CONSTANTS.keys():
            raise dhcp_relay.exceptions.PktTypeError(
                "Invalid DHCP packet type: {pkt_type}. Choose between: {pkt_type_list}.".format(
                    pkt_type=pkt_type,
                    pkt_type_list=', '.join(self.DHCPLIB_CONSTANTS.keys())
                )
            )
        packet = DhcpPacket()
        packet.SetOption("op", [self.DHCPLIB_CONSTANTS.get(pkt_type, {}).get('op', 1)])  # REQUEST
        # See http://www.iana.org/assignments/arp-parameters/arp-parameters.xhtml
        # htype 29 : IP and ARP over ISO 7816-3
        packet.SetOption("htype", [29])  #
        packet.SetOption("hlen", [6])  # Hardware address length
        packet.SetOption("hops", [self.MAX_HOPS])  # Number of hops
        packet.SetOption("giaddr", self._client_ip_address_pydhcplib)
        packet.SetOption("xid", xid)  # Transaction ID
        packet.SetOption("dhcp_message_type", [self.DHCPLIB_CONSTANTS.get(pkt_type).get('dhcp_message_type')])
        packet.SetOption("server_identifier", self._server_identifier_pydhcplib)
        if mac:
            packet.SetOption("chaddr", pydhcplib.type_hw_addr.hwmac(mac).list() + [0] * 10)  # Client hardware address
            packet.SetOption("host_name", pydhcplib.type_strlist.strlist(mac).list())
            packet.SetOption("client_identifier", pydhcplib.type_strlist.strlist(mac).list())

        return packet

    def _send_packet(self, pkt):
        if (time.time() - self.last_pkt_sent) < self.DDOS_RATE_TIME_DIFF:
            time.sleep((self.last_pkt_sent+self.DDOS_RATE_TIME_DIFF) - time.time())
        send_result = self.SendDhcpPacketTo(
            pkt,
            self.SERVER_IP,
            self.SERVER_PORT
        )
        self.last_pkt_sent = time.time()
        return send_result

    def _basic_sender_with_rid(self,
                               pkt_type,
                               rid,
                               xid,
                               mac,
                               ip=None):
        if self._logger is not None and self.LOGGING_ENABLED:
            self._logger.info(
                "Received request #{rid} to send {pkt_type} packet for MAC Address: {mac}, using XID: {xid}".format(
                    rid=rid,
                    mac=str(mac),
                    xid=str(xid),
                    pkt_type=pkt_type
                )
            )
        if not dhcp_relay.util.check_xid(xid):
            if self._logger is not None and self.LOGGING_ENABLED:
                self._logger.error(
                    "Invalid XID ({xid}) for request #{rid}".format(
                        rid=rid,
                        xid=str(xid)
                    )
                )
            return False
        if not dhcp_relay.util.check_mac_address(mac):
            if self._logger is not None and self.LOGGING_ENABLED:
                self._logger.error(
                    "Invalid MAC Address ({mac}) for request #{rid}".format(
                        rid=rid,
                        mac=str(mac)
                    )
                )
            return False
        try:
            packet = self._build_basic_pkt(pkt_type=pkt_type, xid=xid, mac=mac)
            if pkt_type == 'DHCPDISCOVER' and dhcp_relay.util.check_ip_address(ip):
                packet.SetOption("request_ip_address", pydhcplib.type_ipv4.ipv4(ip).list()) # Requested IP address
            self._send_packet(packet)
        except Exception as e:
            if self._logger is not None and self.LOGGING_ENABLED:
                self._logger.error(
                    "Cannot send {pkt_type} for request #{rid}. Cause: {err}".format(
                        rid=rid,
                        err=str(e),
                        pkt_type=pkt_type
                    )
                )
            return False
        if self._logger is not None and self.LOGGING_ENABLED:
            log_message = "{pkt_type} sent for request #{rid}.".format(
                rid=rid,
                pkt_type=pkt_type
            )
            if self.DETAILED_LOG:
                log_message += '\nPacket structure:\n{pkt}'.format(
                    pkt=packet.str()
                )
            self._logger.info(log_message)
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
        if self._logger is not None and self.LOGGING_ENABLED:
            self._logger.info(
                "Received request to send DHCPREQUEST packet for MAC Address: {mac}, using XID: {xid}".format(
                    mac=str(mac),
                    xid=str(xid)
                )
            )
        if not dhcp_relay.util.check_xid(xid):
            if self._logger is not None and self.LOGGING_ENABLED:
                self._logger.error(
                    "Invalid XID ({xid})".format(
                        xid=str(xid)
                    )
                )
            return False
        if not dhcp_relay.util.check_mac_address(mac):
            if self._logger is not None and self.LOGGING_ENABLED:
                self._logger.error(
                    "Invalid MAC Address ({mac}) for XID {xid}".format(
                        xid=xid,
                        mac=str(mac)
                    )
                )
            return False
        if not dhcp_relay.util.check_ip_address(ip):
            if self._logger is not None and self.LOGGING_ENABLED:
                self._logger.error(
                    "Invalid IP Address ({ip}) for XID {xid}".format(
                        xid=xid,
                        ip=str(ip)
                    )
                )
            return False
        try:
            packet = self._build_basic_pkt(pkt_type='DHCPREQUEST', xid=xid, mac=mac)
            packet.SetOption("request_ip_address", ip)
            packet.SetOption("ip_address_lease_time", lease_time)
            self._send_packet(packet)
        except Exception as e:
            if self._logger is not None and self.LOGGING_ENABLED:
                self._logger.error(
                    "Cannot send DHCPREQUEST for XID {xid}. Cause: {err}".format(
                        err=str(e),
                        xid=str(xid)
                    )
                )
            return False
        if self._logger is not None and self.LOGGING_ENABLED:
            log_message = "DHCPREQUEST sent for XID: {xid}.".format(
                xid=str(xid)
            )
            if self.DETAILED_LOG:
                log_message += '\nPacket structure:\n{pkt}'.format(
                    pkt=packet.str()
                )
            self._logger.info(log_message)
        return True

    def send_release(self,
                     rid,
                     xid,
                     mac):
        return self._basic_sender_with_rid('DHCPRELEASE', rid, xid, mac)
