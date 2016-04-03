#!/usr/bin/python


# std lib
from time import time
from time import sleep
from hashlib import md5
from random import randrange

# local modules
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

        # to generate a random Request ID

        return md5(str(time())).hexdigest()


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


    def bring_subscriber_up(self, mac, ip=None):

        if not self.send_discover(mac, ip):
            return False

        start_time = time()

        # TODO: this is awful
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
            self.send_discover(mac)
            count += 1
            if count >= self.DDOS_PROTOCOL_VIOLATION_RATE:
                sleep(1)  # TODO: this is awful too
                count = 0

        return True


    def send_release(self, mac):

        _xid = self._xid()
        _rid = self._rid()

        self._pkt_crafter.send_release(_rid, _xid, mac)


    def bring_subscriber_down(self, mac):

        self.send_release(mac)

        return True
