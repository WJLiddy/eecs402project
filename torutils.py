import socks
import socket
import requests
import stem
from stem import CircStatus
from stem.control import Controller

def get_tor_controller():
	controller = Controller.from_port()
	controller.authenticate()
	# leave stream management to us. That is, let us build our own connections. Don't let Tor decide for us.
	controller.set_conf('__LeaveStreamsUnattached', '1')
	return controller

# Pass in a controller, returns a list of IPs on tor network that traffic will go through.
# If you pass in a list of IP's it will use those.
def set_circuit(controller):

	# Build a new circuit. Sometimes this fails and times out: that's ok, just try again.
	while True:
		try:
			circuit_id = controller.new_circuit(await_build = True)
		except stem.CircuitExtensionFailed:
			continue;
		break

def attach_stream(stream):
	if stream.status == 'NEW':
		controller.attach_stream(stream.id, circuit_id)


