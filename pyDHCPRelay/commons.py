#!/usr/bin/python


class DHCPCommons(object):

    # common objects across listener instances
    xid_mac_map = dict()
    subs_up = dict()
    mac_ip_map= dict()

    last_pkt_sent = 0

    def __init__(self):

        pass
