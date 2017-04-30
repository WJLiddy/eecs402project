# You will have to set up your Tor relay as documented here
# https://stem.torproject.org/tutorials/the_little_relay_that_could.html
import socks
import socket
import requests
import stem
from stem import CircStatus
from stem.control import Controller
from torutils import *
import time

SOCKS_PORT = 9050
CONTROL_PORT = 9051

ANALYSIS_NODE_IP = '129.22.150.52'
ANALYSIS_NODE_PORT = 18089


# Send the tor fingerprints to the server
def send_tor_circuit_fingerprints(fps):
	print "creating socket"
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print "trying connection..."
	s.connect((ANALYSIS_NODE_IP, ANALYSIS_NODE_PORT))
	print "connected!"
	for index, fp in enumerate(fps):
		s.send(fp)
		if(index != len(fp) - 1):
			s.send(",")
	s.close()


# Reroute all traffic through tor
controller = get_tor_controller()
socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_SOCKS5, addr="127.0.0.1", port=9050)
socket.socket = socks.socksocket


while True:
	callback = None
	try:
		print "Setting up a new circuit..."
		fingerprints, callback = set_circuit(controller)
		print "Circuit set up with these fingerprints:"
		print fingerprints
		print "Now sending fingerprints for analysis..."
		send_tor_circuit_fingerprints(fingerprints)
		print "Sent! Going to download the file for 10 seconds, then wait for 15 seconds."
		print "downloading..."
		download_file(FILE_URL,10)
		print "done!"
		sleep(15)
	finally:
		# Stop listening for attach stream events and stop controlling streams
		controller.remove_event_listener(callback)
		controller.reset_conf('__LeaveStreamsUnattached')
controller.close()