# You will have to set up your Tor relay as documented here
# https://stem.torproject.org/tutorials/the_little_relay_that_could.html
import socks
import socket
import requests
import stem
from stem import CircStatus
from stem.control import Controller
from torutils import *
from time import sleep
import sys
import random

SOCKS_PORT = 9050
CONTROL_PORT = 9051

ANALYSIS_NODE_IP = "54.236.62.142"
ANALYSIS_NODE_PORT = 18089

RUNS = 2

# Send the tor fingerprints to the server
def send_tor_circuit_fingerprints(fps):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ANALYSIS_NODE_IP, ANALYSIS_NODE_PORT))
	for index, fp in enumerate(fps):
		s.send(fp)
		if(index != len(fp) - 1):
			s.send(",")
	s.close()


# Reroute all traffic through tor
no_proxy = socket.socket
controller = get_tor_controller()
socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_SOCKS5, addr="127.0.0.1", port=9050)



# Load nodes to put load on from list. 
# Pass file as command line arg
with open(str(sys.argv[1]),'r') as f:
	output = f.read()
target_nodes = output.split(',')

with open(str(sys.argv[2]),'r') as f:
	output = f.read()
routing_nodes = output.split(',')

for node in target_nodes:
	print node

for node in target_nodes:
	for run in range(RUNS):
		callback = None
		try:
			print "Setting up a new circuit..."
			socket.socket = socks.socksocket
			fingerprints, callback = set_circuit(controller,[node, random.choice(routing_nodes),random.choice(routing_nodes)])
			print "Circuit set up with these fingerprints:"
			print fingerprints
			print "Now sending fingerprints for analysis..."
			#socket.socket = no_proxy
			#send_tor_circuit_fingerprints(fingerprints)
			#socket.socket = socks.socksocket
			print "Sent! Going to download the file for 60 seconds, then wait for 70 seconds."
			print "downloading..."
			download_file(FILE_URL,2)
			print "done!"
			sleep(2)
		finally:
			# Stop listening for attach stream events and stop controlling streams
			controller.remove_event_listener(callback)
			controller.reset_conf('__LeaveStreamsUnattached')
controller.close()