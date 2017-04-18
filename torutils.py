import socks
import socket
import requests
import stem
from stem import CircStatus
from stem.control import Controller
import calendar
import time

FILE_URL = "https://landsat-pds.s3.amazonaws.com/L8/139/045/LC81390452014295LGN00/LC81390452014295LGN00_B8.TIF"


def get_tor_controller():
	controller = Controller.from_port()
	controller.authenticate()
	# leave stream management to us. That is, let us build our own connections. Don't let Tor decide for us.
	controller.set_conf('__LeaveStreamsUnattached', '1')
	return controller


def set_analysis_circuit(controller,fp):

	# Build a new circuit. Sometimes this fails and times out: that's ok, just try again.
	while True:
		try:
			circuit_id = controller.new_circuit(path=[fp,"1D59F32D85B5B90487EF85F8614726F1C8CFFF98"],await_build = True)
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
		if descriptor:
			print descriptor.address
		else:
			raise RuntimeError("FATAL ERROR: Unable to determine the address of some node")
	return attach_stream


# Pass in a controller, returns a list of IPs on tor network that traffic will go through.
def set_circuit(controller):

	# Build a new circuit. Sometimes this fails and times out: that's ok, just try again.
	while True:
		try:
			circuit_id = controller.new_circuit(await_build = True)
		except stem.CircuitExtensionFailed:
			continue;
		break

	circ = controller.get_circuit(circuit_id)

# Little helper method to attach a stream to a controller. needed for fn callback
	def attach_stream(stream):
		if stream.status == 'NEW':
			controller.attach_stream(stream.id, circuit_id)

	print "--Path has %s nodes--" % (len(circ.path))

	controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)


	node_ips = []
	node_fingerprints = []

	for node in circ.path:
		fingerprint = node[0]
		descriptor = controller.get_network_status(fingerprint, None)
		if descriptor:
			node_ips.append((descriptor.address))
			node_fingerprints.append((descriptor.fingerprint))
		else:
			raise RuntimeError("FATAL ERROR: Unable to determine the address of some node")
	return [node_ips, node_fingerprints, attach_stream]


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




