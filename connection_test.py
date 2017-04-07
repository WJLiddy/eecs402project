# You will have to set up your Tor relay as documented here
# https://stem.torproject.org/tutorials/the_little_relay_that_could.html

import socks
import socket
import requests
import stem
from stem import CircStatus
from stem.control import Controller


SOCKS_PORT = 9050
CONTROL_PORT = 9051
CONNECTION_TIMEOUT = 30  # timeout before we give up on a circuit
TEST_URL = "https://icanhazip.com"
FILE_URL = "https://landsat-pds.s3.amazonaws.com/L8/139/045/LC81390452014295LGN00/LC81390452014295LGN00_B8.TIF"


# Helper function to download a file
def download_file(url):
	local_filename = url.split('/')[-1]
	r = requests.get(url, stream=True)

	kb_downloaded = 0
	with open(local_filename, 'wb') as f:
		for chunk in r.iter_content(chunk_size=1024): 
			if chunk: # filter out keep-alive new chunks
				f.write(chunk)
				kb_downloaded += 1
				if kb_downloaded % 500 == 0:
					print "%s MB downloaded" % (kb_downloaded / 1000.0)

with Controller.from_port() as controller:
	controller.authenticate()
	# leave stream management to us. That is, let us build our own connections. Don't let Tor decide for us.
	controller.set_conf('__LeaveStreamsUnattached', '1')
	# Build a new circuit
	circuit_id = controller.new_circuit(await_build = True)

	# Attach our stream to it
	def attach_stream(stream):
		if stream.status == 'NEW':
			controller.attach_stream(stream.id, circuit_id)
	controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)

	# OK! At this point, we have built our circuit. Now, we need to go ahead and find all the nodes we used.
	circ = controller.get_circuit(circuit_id)

	print "--Path has %s nodes--" % (len(circ.path))
	for node in circ.path:
		fingerprint = node[0]
		descriptor = controller.get_network_status(fingerprint, None)
		if descriptor:
			print "%s" % (descriptor.address)
		else:
			print "Unable to determine the address of some node"

	try:
		print "Rerouting traffic through Tor..."
		socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_SOCKS5, addr="127.0.0.1", port=9050)
		socket.socket = socks.socksocket
		print "connected!"
		print requests.get(TEST_URL).text
		print "trying to download.."
		download_file(FILE_URL)
		print "done!"
	finally:
		# Stop listening for attach stream events and stop controlling streams
		controller.remove_event_listener(attach_stream)
		controller.reset_conf('__LeaveStreamsUnattached')