#!/usr/bin/python


class DHCPGlobals(object):


	DHCP_SERVER_IP_ADDRESS = "172.20.0.3"
	DHCP_CLIENT_IP_ADDRESS = "192.168.4.204"
	DHCP_SERVER_IDENTIFIER = "172.20.8.1"

	DHCP_SERVER_PORT = 67
	DHCP_CLIENT_PORT = 67

	MAX_HOPS = 5

	DDOS_PROTOCOL_VIOLATION_RATE = 30

	DHCP_LEASE_TIME = 24 * 3600

	DUMMY_IP_ADDRESS = "172.17.27.100"

	LOG_DIRECTORY = '/var/log/NOC/'

	LOGGING_ENABLED = True

	DETAILED_LOG = True

	MAX_WAIT_TIME = 3 # seconds


	######################
	# DO NOT MODIFY THIS:
	######################

	DHCPLIB_CONSTANTS = {
		'DHCPDISCOVER': {
			'op'				: 1,
			'dhcp_message_type'	: 1
		},
		'DHCPREQUEST': {
			'op'				: 1,
			'dhcp_message_type'	: 3
		},
		'DHCPRELEASE': {
			'op'				: 1,
			'dhcp_message_type'	: 7
		}
	}

	######################


	def __init__(self):
		pass
