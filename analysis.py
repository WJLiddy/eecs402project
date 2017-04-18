# You will have to set up your Tor relay as documented here
# https://stem.torproject.org/tutorials/the_little_relay_that_could.html
import socks
import socket
import requests
import stem
from stem import CircStatus
from stem.control import Controller
import calendar
import time
from torutils import *

SOCKS_PORT = 9050
CONTROL_PORT = 9051
DEBUG = True
ANALYSIS_MACHINE_PORT = 44106
CLIENT_MACHINE_IP = "localhost"

def recv_tor_circuit_ips():
	print "waiting to recieve..."
	BUFFER_SIZE = 1024
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(("localhost", ANALYSIS_MACHINE_PORT))
	while True:
		s.listen(1)
		conn, addr = s.accept()
		print 'Connection address:', addr
		if(addr != CLIENT_MACHINE_IP):
			conn.close()
			continue
		data = conn.recv(BUFFER_SIZE)
		print "received data:", data
		conn.close()
		return data.split(',')


#controller = get_tor_controller()

# Reroute traffic through tor
# socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_SOCKS5, addr="127.0.0.1", port=9050)
# socket.socket = socks.socksocket

while True:
	ips = recv_tor_circuit_ips()
	callback = None
	#ry:
	#ips, callback = set_circuit(controller)
	#print ips
	#send_tor_circuit_ips(ips)
	#print "trying to download.."
	#download_file(FILE_URL,1)
	#print "done!"
	#finally:
	# Stop listening for attach stream events and stop controlling streams
	#controller.remove_event_listener(callback)
	#controller.reset_conf('__LeaveStreamsUnattached')
	#controller.close()
