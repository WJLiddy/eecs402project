# You will have to set up your Tor relay as documented here
# https://stem.torproject.org/tutorials/the_little_relay_that_could.html
import socks
import socket
import requests
import stem
from stem import CircStatus
from stem.control import Controller
from torutils import *

SOCKS_PORT = 9050
CONTROL_PORT = 9051

def send_tor_circuit_fingerprints(fps):
	print "Sending ips for analysis"
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect(('129.22.150.52', 18089))

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print "connected!"
	for index, fp in enumerate(fps):
		s.send(fp)
		if(index != len(fp) - 1):
			s.send(",")
	print "done!"
	s.close()

controller = get_tor_controller()

# Reroute traffic through tor
socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_SOCKS5, addr="127.0.0.1", port=9050)
socket.socket = socks.socksocket

while True:
	callback = None
	try:
		ips, fingerprints, callback = set_circuit(controller)
		print ips
		print fingerprints
		send_tor_circuit_fingerprints(fingerprints)
		print "trying to download.."
		download_file(FILE_URL,1)
		print "done!"
	finally:
		# Stop listening for attach stream events and stop controlling streams
		controller.remove_event_listener(callback)
		controller.reset_conf('__LeaveStreamsUnattached')
controller.close()
