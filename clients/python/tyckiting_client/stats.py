import logging
import os.path
import json
import fcntl

class GameStats(object):

	def __init__(self, friendlyBotIds, teamName, enemyName):
		self.friendlyBotIds = friendlyBotIds
		self.enemyName = enemyName
		self.teamName = teamName

		self.moveCount = 0
		self.radarCount = 0
		self.radarHit = 0
		self.shotCount = 0
		self.hitCount = 0
		self.gotHitCount = 0
		self.selfHitCount = 0
		self.detected = 0
	
	def analyzeEvent(self, event):
		if event.event == 'hit':
			logging.info('Hit bot %d', event.bot_id)
			if event.bot_id in self.friendlyBotIds:
				logging.info('outch, selfhit')
				self.selfHitCount += 1
				self.gotHitCount -= 1
			else:
				self.hitCount += 1
		elif event.event == 'die':
			logging.info('Bot %d died (%s)', event.bot_id,
				'team' if event.bot_id in self.friendlyBotIds else 'enemy')
		elif event.event == 'see':
			self.radarHit += 1
			self.detected += 1
		elif event.event == 'radarEcho':
			self.radarHit += 1
		elif event.event == 'detected':
			self.detected += 1
		elif event.event == 'damaged':
			self.gotHitCount += 1
		elif event.event == 'move':
			pass
		elif event.event == 'noaction':
			logging.warning('noaction by bot %d', event.bot_id)

	def analyzeAction(self, action):
		if action.type == 'move':
			self.moveCount += 1
		elif action.type == 'radar':
			self.radarCount += 1
			logging.info('Radar at (%d,%d)', action.x, action.y)
		elif action.type == 'cannon':
			self.shotCount += 1
			logging.info('Shoot at (%d,%d)', action.x, action.y)

	def writeToFile(self, result):
		filename = 'logs/' + self.teamName + '.txt'
		data = {}
		if not os.path.exists(filename):
			open(filename, 'a').close()
		file = open(filename, 'r+')
		fcntl.flock(file, fcntl.LOCK_EX)
		content = file.read()
		if content:
			data = json.loads(content)
		self.addGameStats(data, result)
		file.seek(0)
		file.write(json.dumps(data))
		file.truncate()
		fcntl.flock(file, fcntl.LOCK_UN)
		file.close()

	def addGameStats(self, data, result):
		stats = data.setdefault(self.enemyName, {})
		totalStats = data.setdefault('total', {})
		for key,value in self.toDict().items():
			origValue = stats.setdefault(key, 0)
			stats[key] = origValue + value
			origValue = totalStats.setdefault(key, 0)
			totalStats[key] = origValue + value
		games = stats.setdefault('games', 0)
		stats['games'] = games + 1
		games = totalStats.setdefault('games', 0)
		totalStats['games'] = games + 1
		if result == 'win':
			wins = stats.setdefault('wins', 0)
			stats['wins'] = wins + 1
			wins = totalStats.setdefault('wins', 0)
			totalStats['wins'] = wins + 1

	def toDict(self):
		return {
			'moveCount': self.moveCount,
			'radarCount': self.radarCount,
			'radarHit': self.radarHit,
			'shotCount': self.shotCount,
			'hitCount': self.hitCount,
			'gotHitCount': self.gotHitCount,
			'selfHitCount': self.selfHitCount,
			'detected': self.detected,
		}

	def __str__(self):
		return '####Stats####\n \
		Shots fired:\t{3}\n \
		Shots hit:\t{4}\n \
		Selfhits:\t{6}\n \
		\n \
		Got hit:\t{5}\n \
		Moved:\t\t{0}\n \
		Got detected:\t{7} \
		\n \
		Radared:\t{1}\n \
		Enemies found:\t{2}'.format(
			self.moveCount,
			self.radarCount,
			self.radarHit,
			self.shotCount,
			self.hitCount,
			self.gotHitCount,
			self.selfHitCount,
			self.detected)

class OverallStats(object):

	def __init__(self, name):
		self.filename = 'logs/' + name + '.txt'
		self.data = {}
		if os.path.exists(self.filename):
			self.loadFromFile(self.filename)

	def loadFromFile(self, filename):
		with open(filename, 'r') as file:
			self.data = json.loads(file.readline())

	def writeToFile(self):
		with open(self.filename, 'w') as file:
			file.write(json.dumps(self.data))



