
class GameStats(object):

	def __init__(self, friendlyBotIds):
		self.friendlyBotIds = friendlyBotIds
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
			if event.bot_id in self.friendlyBotIds:
				self.selfHitCount += 1
				self.gotHitcount -= 1
			else:
				self.hitCount += 1
		elif event.event == 'die':
			pass
		elif event.event == 'see':
			self.radarHit += 1
			self.detected += 1
		elif event.event == 'radarEcho':
			self.radarHit += 1
		elif event.event == 'detected':
			self.detected += 1
		elif event.event == 'damaged':
			self.gotHitcount += 1
		elif event.event == 'move':
			pass
		elif event.event == 'noaction':
			logging.warning('noaction by bot %d', event.bot_id)

	def analyzeAction(self, action):
		if action.type == 'move':
			self.moveCount += 1
		elif action.type == 'radar':
			self.radarCount += 1
		elif action.type == 'cannon':
			self.shotCount += 1

	def writeToFile(self, result, teamName):
		pass

	def __str__(self):
		return '####Stats####\n \
		Shots fired:\t{3}\n \
		Shots hit:\t{4}\n \
		Selfhits:\t{6}\n \
		\n \
		Got hit:\t{5}\n \
		Moved:\t{0}\n \
		\n \
		Radared:\t{1}\n \
		Enemies found:\t{3}'.format(
			self.moveCount,
			self.radarCount,
			self.radarHit,
			self.shotCount,
			self.hitCount,
			self.gotHitCount,
			self.selfHitCount,
			self.detected)

class OverallStats(object):

	def test():
		pass
