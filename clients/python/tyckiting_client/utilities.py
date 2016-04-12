import time
import logging

def log_execution_time(function):
	def new_function(*args, **kwargs):
		start = time.time()
		result = function(*args, **kwargs)
		end = time.time()
		logging.info('execution of {:s}: {:f}ms'.format(function.__name__, (end-start)*1000))
		return result
	return new_function