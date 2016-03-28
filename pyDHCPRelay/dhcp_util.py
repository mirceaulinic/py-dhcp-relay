#!/usr/bin/python


import string


ALL_CHARS = ''.join(chr(c) for c in range(256))
DEL_CHARS = set(ALL_CHARS) - set(string.hexdigits)


def check_mac_address(mac_address):

	global ALL_CHARS
	global DEL_CHARS

	mac_address = mac_address.translate(''.join(ALL_CHARS), ''.join(DEL_CHARS))
	if len(mac_address) == 12: # MAC Address has always 12 HEX chars
		return True

	return False


def check_xid(xid):

	if not len(xid) == 4:
		return False
	if not(0 <= xid[0] <= 255 and 0 <= xid[1] <= 255 and 0 <= xid[2] <= 255 and 0 <= xid[3] <= 255):
		return False

	return True


def check_ip_address(ip_address):

	return True
