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


# ports to interface with tor.
SOCKS_PORT = 9050
CONTROL_PORT = 9051

# IP of the machine that is going to send us IPs- ignore every other IP.
CLIENT_MACHINE_IP = '192.22.150.112'

def recv_tor_circuit_ips():
	print "waiting to recieve..."
	BUFFER_SIZE = 1024
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(('', 18089))
	s.listen(5)
	while True:
		print "listening...."
		conn, addr = s.accept()
		print 'Connection address:', addr
		if(addr != CLIENT_MACHINE_IP):
			conn.close()
			continue
		data = conn.recv(BUFFER_SIZE)
		print "received data:", data
		conn.close()
		return data.split(',')



# Reroute traffic through tor
controller = get_tor_controller()
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
socket.socket = socks.socksocket



while True:
	fps = recv_tor_circuit_ips()

	# Sample IPs: [u'38.229.70.53', u'91.134.139.215', u'204.85.191.30']
	#fps = ['7ED90E2833EE38A75795BA9237B0A4560E51E1A0']
	
	callback = None
	for fp in fps:
		try:
			print "Setting up analysis circuit..."
			callback = set_analysis_circuit(controller,fp)
			print "collecting RTTs for 20 seconds..."

			start_time =  calendar.timegm(time.gmtime())
			while calendar.timegm(time.gmtime()) < start_time + 20:
				print "sending HTTP request..."
				start_req =  time.clock()
				print requests.get(BOUNCE_URL, stream=True)
				end_req = time.clock() - start_req 
				print "RTT was " + str(end_req)
		finally:
			# Stop listening for attach stream events and stop controlling streams
			controller.remove_event_listener(callback)
			controller.reset_conf('__LeaveStreamsUnattached')

controller.close()

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
