import sys
import argparse
import subprocess
from time import sleep
import os

def parseArguments():
	parser = argparse.ArgumentParser(description="Starts server and client for the ultimate fight",
		epilog='Example of use:\n' + \
				'run.[py|sh] berta mona --verbose\n' + \
				'run.[py|sh] berta mona --verbose --wait=1000\n' + \
				'run.[py|sh] berta mona --headless --iterations=30',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		prog='run.[sh|py]')
	parser.add_argument('ai_1', metavar='ai_1', type=str,
						help='Name of bot #1')
	parser.add_argument('ai_2', metavar='ai_2', type=str,
				  		help='Name of bot #2')
	parser.add_argument('-v', '--verbose', action='store_true',
						help="Verbose output for ai_2")
	parser.add_argument('-V', '--verbose2', action='store_true',
						help="More Verbose output for ai_2")
	#parser.add_argument('-H', '--headless', action='store_true',
	#					help="runs without waiting and without the spectator")
	parser.add_argument('-i', '--iterations', type=int, default=1, metavar='n',
						help="specifies number of fights; default is 1")
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

def startClients(args):
	os.chdir('clients/python')
	command = ['python3', 'cli.py']
	ai_1_cmd = command + ['--ai=' + args.ai_1, '--name=' + args.ai_1]
	ai_2_cmd = command + ['--ai=' + args.ai_2, '--name=' + args.ai_2]
	if args.verbose2:
		ai_2_cmd.append('--verbose2')
	elif args.verbose:
		ai_2_cmd.append('--verbose')
	with open(os.devnull, 'w') as devnull:
		subprocess.Popen(ai_1_cmd, stdout=devnull)
	subprocess.call(ai_2_cmd)
	os.chdir('../..')

def startGame(args):
	browserCmd = getBrowserCmd()
	startServer(args)
	sleep(0.5)
	startSpectator()
	sleep(3)
	startClients(args)
	sleep(0.1)

if __name__ == '__main__':
	args = parseArguments()
	print(args)
	for i in range(args.iterations):
		startGame(args)
