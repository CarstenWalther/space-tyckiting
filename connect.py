import sys
import argparse
import subprocess
from time import sleep
import os

def parseArguments():
	parser = argparse.ArgumentParser(description="Connect with bot to server",
		epilog='Example of use:\n' + \
				'connect.[py|sh] berta -H=localhost -P=1337\n',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		prog='connect.[sh|py]')
	parser.add_argument('ai_1', metavar='ai_1', type=str,
						help='Name of bot #1')
	parser.add_argument('-v', '--verbose', action='store_true',
						help="Verbose output for ai_1")
	parser.add_argument('-H', '--host', type=str, default='localhost', metavar='host',
						help='time in milliseconds between two rounds')
	parser.add_argument('-P', '--port', type=str, default='3000', metavar='port',
						help='time in milliseconds between two rounds')
	#parser.add_argument('-H', '--headless', action='store_true',
	#					help="runs without waiting and without the spectator")
	#parser.add_argument('-w', '--wait', type=int, default=300, metavar='t',
	#					help='time in milliseconds between two rounds')
	return parser.parse_args()

def getBrowserCmd():
	platform = subprocess.check_output(["uname"]).strip().decode('utf-8')
	if platform == 'Linux':
		return 'gnome-open'
	elif platform == 'Darwin':
		return 'open'
	else:
		print('could not recognize platform')
		sys.exit(1)

def generateServerParameters(args):
	params = []
	return params
	#params += ['--delay', str(args.wait)]
	if args.headless:
		params += ['--overdrive', 'true']
	return params


def startSpectator():
	spectator_url = 'http://' + host + ':' + port + '/'
	browserCmd = getBrowserCmd()
	subprocess.Popen([browserCmd, spectator_url])

def startClient(args):
	os.chdir('clients/python')
	command = ['python3', 'cli.py']
	ai_1_cmd = command + ['--ai=' + args.ai_1, '--name=' + args.ai_1, '--host=' + args.host, '--port=' + args.port]

	if args.verbose:
		ai_1_cmd.append('--verbose')
	subprocess.call(ai_1_cmd)
	os.chdir('../..')

if __name__ == '__main__':
	args = parseArguments()
	print(args)
	startClient(args)
	sleep(0.1)
