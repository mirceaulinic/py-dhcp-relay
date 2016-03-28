#!/usr/bin/python


from pydhcplib.dhcp_packet import *
from pydhcplib.dhcp_network import *
from pydhcplib.type_ipv4 import ipv4
from pydhcplib.type_hw_addr import hwmac
from pydhcplib.type_strlist import strlist

from dhcp_util import *
from dhcp_globals import DHCPGlobals


class DHCPPktCrafter(DHCPGlobals, DhcpClient):


	def __init__(self, logger, force_disable_logging = False):

		DhcpClient.__init__(
			self, 
			self.DHCP_CLIENT_IP_ADDRESS,
			self.DHCP_SERVER_PORT,
			self.DHCP_SERVER_PORT
		)

		self.logger = logger
		self.force_disable_logging = force_disable_logging # to force disabling logging

		self.client_ip_address_pydhcplib = ipv4(self.DHCP_CLIENT_IP_ADDRESS).list()
		self.server_identifier_pydhcplib = ipv4(self.DHCP_SERVER_IDENTIFIER).list()
		# to not compute it when sending every packet


	def build_basic_dhcp_pkt(self, pkt_type, xid, mac = None):

		if pkt_type not in self.DHCPLIB_CONSTANTS.keys():
			raise Exception(
				"Invalid DHCP packet type: {pkt_type}. Choose between: {pkt_type_list}.".format(
					pkt_type 		= pkt_type,
					pkt_type_list 	= ', '.join(self.DHCPLIB_CONSTANTS.keys())
				)
			)

		packet = DhcpPacket()

		packet.SetOption("op", [self.DHCPLIB_CONSTANTS.get(pkt_type).get('op')]) # REQUEST
		# See http://www.iana.org/assignments/arp-parameters/arp-parameters.xhtml
		# htype 29 : IP and ARP over ISO 7816-3
		packet.SetOption("htype", [29]) #
		packet.SetOption("hlen", [6]) # Hardware address length
		packet.SetOption("hops", [self.MAX_HOPS]) # Number of hops
		packet.SetOption("giaddr", self.client_ip_address_pydhcplib)
		packet.SetOption("xid", xid) # Transaction ID

		packet.SetOption("dhcp_message_type", [self.DHCPLIB_CONSTANTS.get(pkt_type).get('dhcp_message_type')])
		packet.SetOption("server_identifier", self.server_identifier_pydhcplib)
		if mac:
			packet.SetOption("chaddr", hwmac(mac).list() + [0] * 10) # Client hardware address
			packet.SetOption("host_name", strlist(mac).list())
			packet.SetOption("client_identifier", strlist(mac).list())

		return packet


	def basic_dhcp_sender_with_rid(self, pkt_type, rid, xid, mac, ip = None):

		if self.LOGGING_ENABLED and not self.force_disable_logging:
			self.logger.info(
				"Received request #{rid} to send {pkt_type} packet for MAC Address: {mac}, using XID: {xid}".format(
					rid 		= rid,
					mac 		= str(mac),
					xid 		= str(xid),
					pkt_type 	= pkt_type
				)
			)

		if not check_xid(xid):
			if self.LOGGING_ENABLED and not self.force_disable_logging:
				self.logger.error(
					"Invalid XID ({xid}) for request #{rid}".format(
						rid = rid,
						xid = str(xid)
					)
				)
			return False

		if not check_mac_address(mac):
			if self.LOGGING_ENABLED and not self.force_disable_logging:
				self.logger.error(
					"Invalid MAC Address ({mac}) for request #{rid}".format(
						rid = rid,
						mac = str(mac)
					)
				)
			return False

		try:
			packet = self.build_basic_dhcp_pkt(pkt_type = pkt_type, xid = xid, mac = mac)
			if pkt_type == 'DHCPDISCOVER' and type(ip) is not None:
				packet.SetOption("request_ip_address", ipv4(ip).list()) # Requested IP address

			self.SendDhcpPacketTo(
				packet,
				self.DHCP_SERVER_IP_ADDRESS,
				self.DHCP_SERVER_PORT
			)
		except Exception as e:
			if self.LOGGING_ENABLED and not self.force_disable_logging:
				self.logger.error(
					"Cannot send {pkt_type} for request #{rid}. Cause: {err}".format(
						rid 		= rid,
						err 		= str(e),
						pkt_type 	= pkt_type
					)
				)
			return False

		if self.LOGGING_ENABLED and not self.force_disable_logging:
			log_message = "{pkt_type} sent for request #{rid}.".format(
				rid 		= rid,
				pkt_type 	= pkt_type
			)
			if self.DETAILED_LOG:
				log_message += '\nPacket structure:\n{pkt}'.format(
					pkt = packet.str()
				)
			self.logger.info(log_message)

		return True


	def send_dhcp_discover(self, rid, xid, mac, ip = None):

		return self.basic_dhcp_sender_with_rid('DHCPDISCOVER', rid, xid, mac, ip)


	def send_dhcp_request(self, xid, mac, ip, lease_time):

		if self.LOGGING_ENABLED and not self.force_disable_logging:
			self.logger.info(
				"Received request to send DHCPREQUEST packet for MAC Address: {mac}, using XID: {xid}".format(
					mac = str(mac),
					xid = str(xid)
				)
			)

		if not check_xid(xid):
			if self.LOGGING_ENABLED and not self.force_disable_logging:
				self.logger.error(
					"Invalid XID ({xid})".format(
						xid = str(xid)
					)
				)
			return False

		if not check_mac_address(mac):
			if self.LOGGING_ENABLED and not self.force_disable_logging:
				self.logger.error(
					"Invalid MAC Address ({mac}) for XID {xid}".format(
						xid = xid,
						mac = str(mac)
					)
				)
			return False

		if not check_ip_address(ip):
			if self.LOGGING_ENABLED and not self.force_disable_logging:
				self.logger.error(
					"Invalid IP Address ({ip}) for XID {xid}".format(
						xid = xid,
						ip = str(ip)
					)
				)
			return False

		try:
			packet = self.build_basic_dhcp_pkt(pkt_type = 'DHCPREQUEST', xid = xid, mac = mac)
			packet.SetOption("request_ip_address", ip)
			packet.SetOption("ip_address_lease_time", lease_time)

			self.SendDhcpPacketTo(
				packet,
				self.DHCP_SERVER_IP_ADDRESS,
				self.DHCP_SERVER_PORT
			)
		except Exception as e:
			if self.LOGGING_ENABLED and not self.force_disable_logging:
				self.logger.error(
					"Cannot send DHCPREQUEST for XID {xid}. Cause: {err}".format(
						err = str(e),
						xid = str(xid)
					)
				)
			return False

		if self.LOGGING_ENABLED and not self.force_disable_logging:
			log_message = "DHCPREQUEST sent for XID: {xid}.".format(
				xid = str(xid)
			)
			if self.DETAILED_LOG:
				log_message += '\nPacket structure:\n{pkt}'.format(
					pkt = packet.str()
				)
			self.logger.info(log_message)

		return True


	def send_dhcp_release(self, rid, xid, mac):

		return self.basic_dhcp_sender_with_rid('DHCPRELEASE', rid, xid, mac, '172.25.170.171')
