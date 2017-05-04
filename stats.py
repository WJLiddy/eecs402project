
# Get all files in results/
from os import listdir
from os.path import isfile, join
import os.path as path

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


result_folders = [f for f in listdir("results/") if path.isdir(join("results/", f))]


for result_folder in result_folders:
	runs = [f for f in listdir("results/" + result_folder) if isfile(join("results/"+result_folder, f))]
	run_avgs = []
	for run in runs:
		with open("results/" + result_folder + "/" + run) as f:
			content = f.readlines()
		content = [line.strip().split(',') for line in content]
		times = []
		for line in content:
			times += [[float(line[0]),float(line[1])]]
		during_download = [i[1] for  i in filter(lambda x: x[0] < 30, times)]
		after_download = [i[1] for  i in filter(lambda x: x[0] >= 30, times)]
		avg_dur = avg(during_download)
		avg_aft = avg(after_download)
		run_avgs += [[avg_dur, avg_aft]]

	result_during, result_after = zip(*run_avgs)
	print "For %s" % result_folder[0:4]
	print "Average RTT during download was " + str(avg(result_during)) + " : " + str(pstdev(result_during))
	print "Average RTT after download was " + str(avg(result_after)) + " : " + str(pstdev(result_after))

