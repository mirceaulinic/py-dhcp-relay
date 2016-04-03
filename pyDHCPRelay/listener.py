#!/usr/bin/python


from threading import Thread

# local modules
from pyDHCPRelay.globals import DHCPGlobals


class DHCPListener(DHCPGlobals, Thread):


    def __init__(self,
                 pkt_crafter,
                 logger=None):

        Thread.__init__(self)

        self._pkt_crafter = pkt_crafter
        self._logger = logger


    def run(self):

        while True:
            received_packet = self._pkt_crafter.GetNextDhcpPacket()
            if received_packet is not None:

                xid = received_packet.GetOption("xid")
                xid_str = '.'.join([str(xid_e) for xid_e in xid])
                mac = self._pkt_crafter.xid_mac_map.get(xid_str)

                pkt_type = ''

                if received_packet.IsDhcpOfferPacket() and mac:

                    pkt_type = 'DHCPOFFER'

                    assigned_ip_address = received_packet.GetOption("yiaddr")
                    lease_time = received_packet.GetOption("ip_address_lease_time")

                    self._pkt_crafter.send_request(
                        xid,
                        mac,
                        assigned_ip_address,
                        lease_time
                    )

                elif received_packet.IsDhcpAckPacket():
                    pkt_type = 'DHCPACK'
                    self._pkt_crafter.xid_mac_map.pop(xid_str, '')
                    if mac:
                        self._pkt_crafter.subs_up[mac] = True

                if self._logger is not None and self.LOGGING_ENABLED:
                    log_message = 'Received {pkt_type} message from AC, for XID: {xid}, corresponding for MAC address: {mac}.'.format(
                        xid=str(xid),
                        mac=str(mac),
                        pkt_type=pkt_type
                    )
                    if self.DETAILED_LOG:
                        log_message += '\nPacket structure:\n{pkt}'.format(
                            pkt=received_packet.str()
                        )
                    self._logger.info(log_message)
