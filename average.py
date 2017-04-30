
# Get all files in results/
from os import listdir
from os.path import isfile, join

# numpy is for losers lmao
def avg(lst):
	return reduce(lambda x, y: x + y, lst) / len(lst)

def _ss(data):
	"""Return sum of square deviations of sequence data."""
	c = avg(data)
	ss = sum((x-c)**2 for x in data)
	return ss

def pstdev(data):
	"""Calculates the population standard deviation."""
	n = len(data)
	if n < 2:
		raise ValueError('variance requires at least two data points')
	ss = _ss(data)
	pvar = ss/n # the population variance
	return pvar**0.5


onlyfiles = [f for f in listdir("results/") if isfile(join("results/", f))]

avgs = []



for file in onlyfiles:
	print file
	with open("results/" + file) as f:
		content = f.readlines()
	content = [line.strip().split(',') for line in content]
	times = []
	for line in content:
		times += [[float(line[0]),float(line[1])]]
	during_download = [i[1] for  i in filter(lambda x: x[0] < 60, times)]
	after_download = [i[1] for  i in filter(lambda x: x[0] >= 60, times)]
	#print during_download
	#print after_download
	avg_dur = avg(during_download)
	avg_aft = avg(after_download)
	#print avg_dur
	#print avg_aft
	avgs += [[avg_dur, avg_aft]]

print avgs
avg_dur_total, avg_dur_after = zip(*avgs)
print str(avg(avg_dur_total)) + " " + str(pstdev(avg_dur_total)) 
print str(avg(avg_dur_after)) + " " + str(pstdev(avg_dur_after))
