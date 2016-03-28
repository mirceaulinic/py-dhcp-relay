#!/usr/bin/python


from threading import Thread

from dhcp_commons import DHCPCommons
from dhcp_globals import DHCPGlobals


class DHCPListener(DHCPCommons, DHCPGlobals, Thread):


	def __init__(self, logger, dhcp_pkt_crafter):

		Thread.__init__(self)
		self.logger = logger
		self.dhcp_pkt_crafter = dhcp_pkt_crafter


	def run(self):

		while True:
			received_packet = self.dhcp_pkt_crafter.GetNextDhcpPacket()
			if received_packet:

				xid 	= received_packet.GetOption("xid")
				xid_str = '.'.join([str(xid_e) for xid_e in xid])
				mac 	= self.xid_mac_map.get(xid_str)

				dhcp_pkt_type = ''

				if received_packet.IsDhcpOfferPacket() and mac:

					dhcp_pkt_type = 'DHCPOFFER'

					assigned_ip_address = received_packet.GetOption("yiaddr")
					lease_time 			= received_packet.GetOption("ip_address_lease_time")

					self.dhcp_pkt_crafter.send_dhcp_request(
						xid, 
						mac, 
						assigned_ip_address, 
						lease_time
					)

				elif received_packet.IsDhcpAckPacket():
					dhcp_pkt_type = 'DHCPACK'
					self.xid_mac_map.pop(xid_str)
					if mac:
						self.subs_up[mac] = True

				if self.LOGGING_ENABLED:
					log_message = 'Received {pkt_type} message from AC, for XID: {xid}, corresponding for MAC address: {mac}.'.format(
						xid 		= str(xid),
						mac 		= str(mac),
						pkt_type 	= dhcp_pkt_type
					)
					if self.DETAILED_LOG:
						log_message += '\nPacket structure:\n{pkt}'.format(
							pkt = received_packet.str()
						)
					self.logger.info(log_message)
