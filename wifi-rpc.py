#!/usr/bin/python


#-*- coding: utf-8 -*-(PEP263)
#title           :WiFi RPC for DHCP Subscibers
#description     :
#author          :Mircea Ulinic
#email           :mircea@ibrowse.com
#version         :0.2
#usage           :python wifi-rpc.py
#notes           :Beta testing
#python_version  :2.7
#==============================================================================


# PING
from ping import verbose_ping

# XML-RPC
from SocketServer import ThreadingMixIn
from DocXMLRPCServer import DocXMLRPCServer

# iBTools
from ibtools.logger import Logger

# DHCP package classes
from dhcp_relay import DHCPRelay
from dhcp_globals import DHCPGlobals
from dhcp_listener import DHCPListener
from dhcp_pkt_crafter import DHCPPktCrafter


# GLOBAL variables
########################################
dhcp_relay_handler = None
########################################
logger = None
########################################


########################################
# XML RPC multi-threading class
########################################
class DocThreadedXMLRPCServer(ThreadingMixIn, DocXMLRPCServer):
	
	'''
	Mutltithreaded version of DocXMLRPCServer
	'''

	pass


########################################
# XML RPC methods
########################################

def create_dhcp_session(mac, ip = None):

	'''
	Creates DHCP subscriber and returns boolean value in case of success.
	Arguments:
		- MAC Address
		- IP Address (optional)
	Returns:
		- boolean value for success of request
	'''

	global logger
	global dhcp_relay_handler

	if type(mac) is not str:
		if DHCPGlobals.LOGGING_ENABLED:
			logger.warning(
				'Method `create_dhcp_session`: Please send a MAC address as string. Received instead: {your_mac}, having type: {your_mac_type}'.format(
					your_mac 		= str(mac),
					your_mac_type 	= str(type(mac))
				)
			)
			return False

	return dhcp_relay_handler.bring_subscriber_up(mac, ip)


def create_dhcp_sessions_bulk(mac_list):

	'''
	Creates DHCP subscribers for a list of MAC Addresses.
	Arguments:
		- List of MAC Addresses
	Returns:
		- True when done
	'''

	global logger
	global dhcp_relay_handler

	if type(mac_list) is not list:
		if DHCPGlobals.LOGGING_ENABLED:
			logger.warning(
				'Method `create_dhcp_sessions_bulk`: Please send a list of MAC addresses. Received instead: {your_mac_list}, having type: {your_mac_list_type}'.format(
					your_mac_list 		= str(mac_list),
					your_mac_list_type 	= str(type(mac_list))
				)
			)
			return False

	return dhcp_relay_handler.bring_subscribers_list_up(mac_list)


def destroy_dhcp_session(mac):

	'''
	Releases DHCP subscriber and returns boolean value in case of success.
	Arguments:
		- MAC Address
	Returns:
		- boolean for success of request
	'''

	global logger
	global dhcp_relay_handler

	if type(mac) is not str:
		if DHCPGlobals.LOGGING_ENABLED:
			logger.warning(
				'Method `destroy_dhcp_session`: lease send a MAC address as string. Received instead: {your_mac}, having type: {your_mac_type}'.format(
					your_mac 		= str(mac),
					your_mac_type 	= str(type(mac))
				)
			)
			return False

	return dhcp_relay_handler.bring_subscriber_down(mac)


if __name__ == '__main__':

	logger = Logger('dhcp_clients', directory = DHCPGlobals.LOG_DIRECTORY)

	verbose_ping(DHCPGlobals.DHCP_SERVER_IP_ADDRESS)

	dhcp_pkt_crafter = DHCPPktCrafter(logger, force_disable_logging = False)
	dhcp_pkt_crafter.BindToAddress()

	dhcp_relay_handler = DHCPRelay(dhcp_pkt_crafter)

	dhcp_listener = DHCPListener(logger, dhcp_pkt_crafter)
	dhcp_listener.start()

	server = DocThreadedXMLRPCServer(("0.0.0.0", 8000), allow_none = True)

	server.register_function(create_dhcp_session)
	server.register_function(create_dhcp_sessions_bulk)
	server.register_function(destroy_dhcp_session)
	server.register_introspection_functions()

	# Run the server's main loop
	server.serve_forever()
