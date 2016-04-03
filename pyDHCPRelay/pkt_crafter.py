#!/usr/bin/python

# third party libs
import pydhcplib

from pydhcplib.dhcp_packet import *
from pydhcplib.dhcp_network import *

# local modules
import pyDHCPRelay.util
import pyDHCPRelay.exceptions

from pyDHCPRelay.globals import DHCPGlobals


class DHCPPktCrafter(DHCPGlobals, DhcpClient):


    def __init__(self,
                 server_address,
                 server_port=67,
                 logger=None):

        self._logger = logger


    def connect():

        DhcpClient.__init__(
            self,
            self.DHCP_CLIENT_IP_ADDRESS,
            self.DHCP_SERVER_PORT,
            self.DHCP_SERVER_PORT
        )

        self._client_ip_address_pydhcplib = pydhcplib.type_ipv4.ipv4(self.DHCP_CLIENT_IP_ADDRESS).list()
        self._server_identifier_pydhcplib = pydhcplib.type_ipv4.ipv4(self.DHCP_SERVER_IDENTIFIER).list()
        # to not compute it when sending every packet


    def _build_basic_pkt(self,
                         pkt_type,
                         xid,
                         mac=None):

        if pkt_type not in self.DHCPLIB_CONSTANTS.keys():
            raise pyDHCPRelay.exceptions.PktTypeError(
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

        if not pyDHCPRelay.util.check_xid(xid):
            if self._logger is not None and self.LOGGING_ENABLED:
                self._logger.error(
                    "Invalid XID ({xid}) for request #{rid}".format(
                        rid=rid,
                        xid=str(xid)
                    )
                )
            return False

        if not pyDHCPRelay.util.check_mac_address(mac):
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
            if pkt_type == 'DHCPDISCOVER' and ip is not None:
                packet.SetOption("request_ip_address", pydhcplib.type_ipv4.ipv4(ip).list()) # Requested IP address

            self.SendDhcpPacketTo(
                packet,
                self.DHCP_SERVER_IP_ADDRESS,
                self.DHCP_SERVER_PORT
            )
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

        if not pyDHCPRelay.util.check_xid(xid):
            if self._logger is not None and self.LOGGING_ENABLED:
                self._logger.error(
                    "Invalid XID ({xid})".format(
                        xid=str(xid)
                    )
                )
            return False

        if not pyDHCPRelay.util.check_mac_address(mac):
            if self._logger is not None and self.LOGGING_ENABLED:
                self._logger.error(
                    "Invalid MAC Address ({mac}) for XID {xid}".format(
                        xid=xid,
                        mac=str(mac)
                    )
                )
            return False

        if not pyDHCPRelay.util.check_ip_address(ip):
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

            self.SendDhcpPacketTo(
                packet,
                self.DHCP_SERVER_IP_ADDRESS,
                self.DHCP_SERVER_PORT
            )
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


    def send_release(self, rid, xid, mac):

        return self._basic_sender_with_rid('DHCPRELEASE', rid, xid, mac)
