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
FILE_URL = "https://landsat-pds.s3.amazonaws.com/L8/139/045/LC81390452014295LGN00/LC81390452014295LGN00_B8.TIF"
ANALYSIS_MACHINE_IP = "129.22.150.52"
ANALYSIS_MACHINE_PORT = 44106

def send_tor_circuit_ips(ips):
	print "Sending ips for analysis"
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ANALYSIS_MACHINE_IP, ANALYSIS_MACHINE_PORT))
	print "connected!"
	for index, ip in enumerate(ips):
		s.send(ip)
		if(index != len(ip) - 1):
			s.send(",")
	print "done!"
	s.close()


# Helper function to download a file, until timeout. 
#If timeout is set to zero, then will finish as soon as file finished downloading.
def download_file(url,timeout = 0):
	start_time =  calendar.timegm(time.gmtime())
	local_filename = url.split('/')[-1]
	# Repeatedly download file until timeout
	while True:
		r = requests.get(url, stream=True)
		kb_downloaded = 0
		with open(local_filename, 'wb') as f:
			for chunk in r.iter_content(chunk_size=1024): 
				if chunk: # filter out keep-alive new chunks
					f.write(chunk)
					# return if time expired (unless timeout is zero)
					if(timeout != 0 and calendar.timegm(time.gmtime()) > start_time + timeout):
						return
					kb_downloaded += 1
					if kb_downloaded % 500 == 0 and DEBUG:
						print "%s MB downloaded" % (kb_downloaded / 1000.0)
		if(timeout == 0):
			return

controller = get_tor_controller()

# Reroute traffic through tor
socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_SOCKS5, addr="127.0.0.1", port=9050)
socket.socket = socks.socksocket

while True:
	callback = None
	try:
		ips, callback = set_circuit(controller)
		print ips
		send_tor_circuit_ips(ips)
		print "trying to download.."
		download_file(FILE_URL,1)
		print "done!"
	finally:
		# Stop listening for attach stream events and stop controlling streams
		controller.remove_event_listener(callback)
		controller.reset_conf('__LeaveStreamsUnattached')
controller.close()
