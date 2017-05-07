# Downloads info about each tor node as json

# You can get all the node info here :  https://onionoo.torproject.org/details

# We want to find the nodes that may slow down under load
# So, we are going to pick the 10 nodes that are probably struggling.

# In the paper, they picked nodes that had low-ish traffic. 
# To do this, we are going to pick tor nodes with low observed bandwidth.

import json
import requests
import os

nodes = json.loads(requests.get('https://onionoo.torproject.org/details').text)

node_scores = []
for node in  nodes["relays"]:
	if not node["running"]:
		continue

	# Some nodes do not report a bandwidth
	# and, many of the nodes I found have suspicously low observed bandwidth. (Like 500 b/s)
	# Maybe this is because they just came online?
	# Regardless, I pick 30 Kb/s as the lowest. That's plenty slow.
	if node["observed_bandwidth"] < 30000:
		continue



	node_scores += [[node["fingerprint"],node["consensus_weight"]]]

print str(len(node_scores)) + " nodes were online"

node_scores = sorted(node_scores, key=lambda n: n[1])

save = open("old_nodes", 'w')
for node in node_scores[len(node_scores)-51 : len(node_scores) - 1]:
	save.write(node[0])
	save.write(",")
save.seek(-1, os.SEEK_END)
save.truncate()
save.close()



save = open("new_nodes", 'w')
for node in node_scores[0:50]:
	save.write(node[0])
	save.write(",")
save.seek(-1, os.SEEK_END)
save.truncate()
save.close()



