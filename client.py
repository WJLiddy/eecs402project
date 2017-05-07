# You will have to set up your Tor relay as documented here
# https://stem.torproject.org/tutorials/the_little_relay_that_could.html
import socks
import socket
import requests
import stem
import signal
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

RUNS = 1

EXIT_NODE = "CBA8B64BCBA9FAFEBB57EFCEC5A8524D1351C7E1"


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
socket.socket = socks.socksocket


# Load nodes to put load on from list. 
# Pass file as command line arg
with open(str(sys.argv[1]),'r') as f:
	output = f.read()
target_nodes = output.split(',')

def signal_handler(signum, frame):
	raise Exception("Creating circuit or request timed out")

for node in target_nodes:
	for run in range(RUNS):
		callback = None
		try:
			signal.signal(signal.SIGALRM, signal_handler)
			# If we haven't finished by now something has gone wrong.
			# It should not take more than 10 s to set up circuit.
			signal.alarm(10 + (2*DOWNLOAD_TIME))

			print "Setting up a new circuit..."
			socket.socket = socks.socksocket
			fingerprints, callback = set_circuit(controller,[node, EXIT_NODE])
			print "Circuit set up. Now sending fingerprints for analysis..."
			socket.socket = no_proxy
			send_tor_circuit_fingerprints(fingerprints)
			socket.socket = socks.socksocket
			print "Sent. Going to download the file now."
			download_file(CLIENT_FILE_URL,DOWNLOAD_TIME)
			print "done."
			sleep(DOWNLOAD_TIME)
		except Exception,e:
			print "This run was aborted, reason:"
			print str(e)
		finally:
			# Stop listening for attach stream events and stop controlling streams
			controller.remove_event_listener(callback)
			controller.reset_conf('__LeaveStreamsUnattached')
controller.close()