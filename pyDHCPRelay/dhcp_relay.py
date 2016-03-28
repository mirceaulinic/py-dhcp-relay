#!/usr/bin/python


from time import time
from time import sleep
from hashlib import md5
from random import randrange

from dhcp_commons import DHCPCommons
from dhcp_globals import DHCPGlobals


class DHCPRelay(DHCPCommons, DHCPGlobals):


	def __init__(self, dhcp_pkt_crafter):

		self.dhcp_pkt_crafter = dhcp_pkt_crafter


	def generate_xid(self):

		xid = [
			randrange(255),
			randrange(255),
			randrange(255),
			randrange(255),
		] # random transaction ID

		return xid


	def generate_rid(self):

		# to generate a random Request ID

		return md5(str(time())).hexdigest()


	def send_dhcp_discover(self, mac, ip = None):

		xid = self.generate_xid()
		rid = self.generate_rid() # Request ID

		xid_str 					= '.'.join([str(xid_e) for xid_e in xid])
		self.xid_mac_map[xid_str] 	= mac
		self.subs_up[mac] 			= False
		if not ip:
			ip = self.DUMMY_IP_ADDRESS
			# if no specific IP Address is requested,
			# will try to request something dummy
			# anyway the DHCP server will asign one...
		return self.dhcp_pkt_crafter.send_dhcp_discover(rid, xid, mac, ip)
		# sends DHCP Discover Packet


	def bring_subscriber_up(self, mac, ip = None):

		if not self.send_dhcp_discover(mac, ip):
			return False

		start_time = time()

		while (not self.subs_up.get(mac) and time() - start_time < self.MAX_WAIT_TIME):
			pass # waiting till subscriber comes up
			# but no more than MAX_WAIT_TIME seconds

		created = self.subs_up.get(mac)

		if created is not None:
			self.subs_up.pop(mac)

		return created


	def bring_subscribers_list_up(self, mac_list):

		count = 0

		for mac in mac_list:
			self.send_dhcp_discover(mac)
			count += 1
			if count >= self.DDOS_PROTOCOL_VIOLATION_RATE:
				sleep(1)
				count = 0

		return True


	def send_dhcp_release(self, mac):

		xid = self.generate_xid()
		rid = self.generate_rid()

		self.dhcp_pkt_crafter.send_dhcp_release(rid, xid, mac)


	def bring_subscriber_down(self, mac):

		self.send_dhcp_release(mac)

		return True
