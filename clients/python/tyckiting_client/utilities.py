import time
import logging


execTimes = dict()

def log_execution_time(function):
	def new_function(*args, **kwargs):
		start = time.time()
		result = function(*args, **kwargs)
		end = time.time()

		execTime = (end-start)*1000
		funcName = function.__name__
		if not funcName in execTimes:
			execTimes[funcName] = []
		
		execTimes[funcName].append(execTime)
		
		logging.info('execution of {:s}: {:f}ms'.format(funcName, execTime))
		return result
	return new_function

def log_execution_time_stats():
	logging.info('Execution Times:')
	funcStats = []

	for func in execTimes:
		totalTime = sum(execTimes[func])
		count = len(execTimes[func])
		avg = totalTime / count
		
		funcStats.append( (totalTime, avg, count, func) )

	funcStats = sorted(funcStats, reverse=True)
	logging.info('{:^12}|{:^12}|{:^12}|{:^12}'.format('total ms', 'avg ms', 'count', 'function'))
	logging.info('-'*51)
	for total, avg, count, func in funcStats:
		func = 'total' if func == 'decide' else func
		logging.info('{: 12.2f}|{: 12.2f}|{: 12.2f}| {:s}'.format(total, avg, count, func))