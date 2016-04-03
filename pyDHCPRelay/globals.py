#!/usr/bin/python


class DHCPGlobals(object):


    DHCP_SERVER_IP_ADDRESS = "172.20.0.3"  # to be set by the user
    DHCP_CLIENT_IP_ADDRESS = "192.168.4.204"  # to get lo0 of the running machine and also allow setter
    DHCP_SERVER_IDENTIFIER = "172.20.8.1"  # by default is DHCP_SERVER_IP_ADDRESS, allows setter

    DHCP_SERVER_PORT = 67  # can be set by the user
    DHCP_CLIENT_PORT = 67

    DUMMY_IP_ADDRESS = "172.17.17.1"

    DHCP_LEASE_TIME = 24 * 3600

    LOG_DIRECTORY = '/var/log/NOC/'

    LOGGING_ENABLED = True

    DETAILED_LOG = True

    LISTENERS = 1

    MAX_WAIT_TIME = 3  # seconds

    DDOS_PROTOCOL_VIOLATION_RATE = 30

    ######################
    # DO NOT MODIFY THIS:
    ######################

    DHCPLIB_CONSTANTS = {
        'DHCPDISCOVER': {
            'op'                : 1,
            'dhcp_message_type' : 1
        },
        'DHCPREQUEST': {
            'op'                : 1,
            'dhcp_message_type' : 3
        },
        'DHCPRELEASE': {
            'op'                : 1,
            'dhcp_message_type' : 7
        }
    }

    ######################


    def __init__(self):
        pass
