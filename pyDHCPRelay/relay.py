#!/usr/bin/python


# std lib
import os
import signal
from time import time
from time import sleep
from hashlib import md5
from functools import wraps
from random import randrange

# local modules
import pyDHCPRelay.exceptions
from pyDHCPRelay.commons import DHCPCommons
from pyDHCPRelay.globals import DHCPGlobals
from pyDHCPRelay.listener import DHCPListener
from pyDHCPRelay.pkt_crafter import DHCPPktCrafter


class DHCPRelay(DHCPCommons, DHCPGlobals):


    def __init__(self,
                 server_address,
                 server_port=67,
                 logger=None):
        self._pkt_crafter = DHCPPktCrafter(server_address, server_port, logger)

        self._logger = logger


    @property
    def client_address(self):
        return self.DHCP_CLIENT_IP_ADDRESS


    @client_address.setter
    def client_address(self, value):
        self.DHCP_CLIENT_IP_ADDRESS = value


    @property
    def server_identifier(self):
        return self.DHCP_SERVER_IDENTIFIER


    @server_identifier.setter
    def server_identifier(self, value):
        self.DHCP_SERVER_IDENTIFIER = value


    @property
    def client_port(self):
        return self.DHCP_CLIENT_PORT


    @client_port.setter
    def client_port(self, value):
        self.DHCP_CLIENT_PORT = value


    @property
    def default_request_address(self):
        return self.DUMMY_IP_ADDRESS


    @default_request_address.setter
    def default_request_address(self, value):
        self.DUMMY_IP_ADDRESS = value


    @property
    def lease_time(self):
        return self.DHCP_LEASE_TIME


    @lease_time.setter
    def lease_time(self, value):
        self.DHCP_LEASE_TIME = value


    @property
    def log_enabled(self):
        return self.LOGGING_ENABLED


    @log_enabled.setter
    def log_enabled(self, value):
        self.LOGGING_ENABLED = value


    @property
    def log_dir(self):
        return self.LOG_DIRECTORY


    @log_dir.setter
    def log_dir(self, value):
        self.LOG_DIRECTORY = value


    @property
    def log_details(self):
        return self.DETAILED_LOG


    @log_details.setter
    def log_details(self, value):
        self.DETAILED_LOG = value


    @property
    def listeners(self):
        return self.LISTENERS


    @listeners.setter
    def listeners(self, value):
        self.LISTENERS = value

    @property
    def timeout(self):
        return self.MAX_WAIT_TIME


    @timeout.setter
    def timeout(self, value):
        self.MAX_WAIT_TIME = value


    @property
    def ddos_limit(self):
        return self.DDOS_PROTOCOL_VIOLATION_RATE


    @ddos_limit.setter
    def ddos_limit(self, value):
        self.DDOS_PROTOCOL_VIOLATION_RATE = value


    def connect():
        self._pkt_crafter.connect()
        _listeners = list()
        for _ in range(DHCPGlobals.LISTENERS):  # start as many listeners as needed
            _listener = DHCPListener(self._pkt_crafter, self._logger)
            _listeners.append(_listener)
        for _listener in _listeners:
            _listener.start()


    @staticmethod
    def _xid():

        _xid = [
            randrange(255),
            randrange(255),
            randrange(255),
            randrange(255),
        ] # random transaction ID

        return _xid


    @staticmethod
    def _rid():
        return md5(str(time())).hexdigest()


    def timeout(wait):
        def wrap_function(func):
            @wraps(func)
            def __wrapper(*args, **kwargs):
                def handler(signum, frame):
                    raise pyDHCPRelay.exceptions.TimeoutException

                old = signal.signal(signal.SIGALRM, handler)
                signal.setitimer(signal.ITIMER_REAL, float(wait) / 1000)
                try:
                    result = func(*args, **kwargs)
                finally:
                    signal.signal(signal.SIGALRM, old)
                return result
            return __wrapper
        return wrap_function


    def send_discover(self, mac, ip=None):

        _xid = self._xid()
        _rid = self._rid()  # Unique Request ID

        _xid_str = '.'.join([str(xid_e) for xid_e in xid])
        self.xid_mac_map[_xid_str] = mac
        self.subs_up[mac] = False
        if not ip:
            ip = self.DUMMY_IP_ADDRESS
            # if no specific IP Address is requested,
            # will try to request something dummy
        return self._pkt_crafter.send_discover(_rid, _xid, mac, ip)
        # sends DHCP Discover Packet


    @timeout(self.MAX_WAIT_TIME)
    def bring_subscriber_up(self, mac, ip=None):

        if not self.send_discover(mac, ip):
            return False

        start_time = time()

        while (not self.subs_up.get(mac, '')):
            continue  # wait till subs comes up

        self.subs_up.pop(mac, '')

        return self.mac_ip_map.pop(mac, '')  # returns the assigned IP Address


    def bring_subscribers_list_up(self, mac_list):

        for mac in mac_list:
            self.send_discover(mac)

        return True


    def send_release(self, mac):

        _xid = self._xid()
        _rid = self._rid()

        self._pkt_crafter.send_release(_rid, _xid, mac)


    def bring_subscriber_down(self, mac):

        self.send_release(mac)

        return True
