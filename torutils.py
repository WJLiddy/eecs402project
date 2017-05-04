import socks
import socket
import requests
import stem
from stem import CircStatus
from stem.control import Controller
import calendar
import time


# fingerprint of our exit node.
OUR_EXIT_NODE_FP =  "2CA4B2F36C2DDECFCB0B5A0D3300ED30E68E2D62"
HOP_FP = "3DC5B80B0FBB7F88B709CB4C388D9CE8D21EF3DC"
# URL to bounce off of. Should be hosted on the exit node, but this works, for now, without incurring too much lag
BOUNCE_URL = "http://54.236.62.142/"

DOWNLOAD_TIME = 30
BUFFER_TIME = 5

# returns a tor controller
def get_tor_controller():
	controller = Controller.from_port()
	controller.authenticate()
	# leave stream management to us. That is, let us build our own connections. Don't let Tor decide for us.
	controller.set_conf('__LeaveStreamsUnattached', '1')
	return controller


# Will make a circuit with the fingerprint that goes through the exit node at the top of this file.
# Retuns a function which Tor needs to clean up later.
def set_analysis_circuit(controller,fp):

	# Build a new circuit. Sometimes this fails and times out: that's ok, just try again.
	while True:
		try:
			circuit_id = controller.new_circuit(path=[fp,HOP_FP,OUR_EXIT_NODE_FP],await_build = True)
		except stem.CircuitExtensionFailed, e:
			print str(e)
			continue;
		break

	circ = controller.get_circuit(circuit_id)

	# Little helper method to attach a stream to a controller. needed for fn callback
	def attach_stream(stream):
		if stream.status == 'NEW':
			controller.attach_stream(stream.id, circuit_id)

	print "--Path has %s nodes--" % (len(circ.path))

	controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)

	for node in circ.path:
		fingerprint = node[0]
		descriptor = controller.get_network_status(fingerprint, None)
		if not descriptor:
			raise RuntimeError("FATAL ERROR: Unable to determine the address of some node")
	return attach_stream


# Pass in a controller, uses TOR to make a circuit.
# Returns fingerprints it chose at well as the function callback needed by tor
def set_circuit(controller, node_fps):

	# Build a new circuit. Sometimes this fails and times out: that's ok, just try again.
	while True:
		try:
			circuit_id = controller.new_circuit(path=node_fps, await_build = True)
		except stem.CircuitExtensionFailed:
			continue;
		break

	circ = controller.get_circuit(circuit_id)

# Little helper method to attach a stream to a controller. needed for fn callback
	def attach_stream(stream):
		if stream.status == 'NEW':
			controller.attach_stream(stream.id, circuit_id)

	controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)

	node_fingerprints = []

	for node in circ.path:
		fingerprint = node[0]
		node_fingerprints.append(fingerprint)
		descriptor = controller.get_network_status(fingerprint, None)
		if not descriptor:
			raise RuntimeError("FATAL ERROR: Unable to determine the address of some node")
	return [node_fingerprints, attach_stream]


# Helper function to download a file, until timeout. 
#If timeout is set to zero, then will finish as soon as file finished downloading.
def download_file(url,timeout = 0):
	start_time =  calendar.timegm(time.gmtime())
	local_filename = url.split('/')[-1]
	# Repeatedly download file until timeout
	while True:
		print "making request..."
		r = requests.get(url, stream=True)
		print "request made!"
		kb_downloaded = 0
		with open(local_filename, 'wb') as f:
			for chunk in r.iter_content(chunk_size=1024): 
				if chunk: # filter out keep-alive new chunks
					f.write(chunk)
					# return if time expired (unless timeout is zero)
					if(timeout != 0 and calendar.timegm(time.gmtime()) > start_time + timeout):
						return
					kb_downloaded += 1
					if kb_downloaded % 500 == 0:
						print "%s MB downloaded" % (kb_downloaded / 1000.0)
		if(timeout == 0):
			return




