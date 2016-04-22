import sys
import argparse
import subprocess
from time import sleep
import os

def parseArguments():
	parser = argparse.ArgumentParser(description="Starts server and client for the ultimate fight",
		epilog='Example of use:\n' + \
				'start_server.[py|sh]\n',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		prog='start_server.[sh|py]')
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

def startServer(args):
	#print(generateServerParameters(args))
	command = ['node', 'server/start-server.js'] + generateServerParameters(args)
	with open(os.devnull, 'w') as devnull:
		subprocess.Popen(command, stdout=devnull)

def startSpectator():
	spectator_url = 'http://localhost:3000/'
	browserCmd = getBrowserCmd()
	subprocess.Popen([browserCmd, spectator_url])

def startGame(args):
	browserCmd = getBrowserCmd()
	startServer(args)
	sleep(0.5)
	startSpectator()
	sleep(3)

if __name__ == '__main__':
	args = parseArguments()
	print(args)
	startGame(args)
