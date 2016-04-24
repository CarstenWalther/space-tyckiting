import time
import logging
import random

COUNT = 0
SUM = 1
MAX = 2

functionStats = dict()

def log_execution_time(function):
	def new_function(*args, **kwargs):
		start = time.time()
		result = function(*args, **kwargs)
		execTime = (time.time() - start) * 1000
		funcName = function.__name__
		stats = functionStats.setdefault(funcName, [0,0,0])
		stats[COUNT] += 1
		stats[SUM] += execTime
		if execTime > stats[MAX]:
			stats[MAX] = execTime
		return result
	return new_function

def log_execution_time_stats():
	logging.info('Execution Times:')
	funcStats = []

	for func,values in functionStats.items():
		totalTime = values[SUM]
		count = values[COUNT]
		maximum = values[MAX]
		avg = totalTime / count
		funcStats.append( (totalTime, avg, maximum, count, func) )

	printExecTimeTable(funcStats)

def printExecTimeTable(funcStats):
	funcStats = sorted(funcStats, reverse=True)
	logging.info('{:^10}|{:^10}|{:^10}|{:^10}|{:^10}'.format('total ms', 'avg ms', 'max ms', 'count', 'function'))
	logging.info('-'*51)
	for total, avg, count, maximum, func in funcStats:
		func = 'total' if func == 'decide' else func
		logging.info('{: 10.2f}|{: 10.2f}|{: 10.2f}|{: 10.2f}| {:s}'.format(total, avg, count, maximum, func))

def chooseByProbability(plist):
	index = 0
	total = sum(p for p, *_ in plist)	
	r = random.uniform(0, total)
	for i, t in enumerate(plist):
		r -= t[0]
		if r < 0:
			index = i
			break
	return (index, plist[index])