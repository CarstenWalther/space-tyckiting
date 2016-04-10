
import logging

from tyckiting_client.hexagon import cube_add
from tyckiting_client import actions
from tyckiting_client import messages

'''
good against random movers and short distance movers
bad vs straight distance 2 movers
needs 3 bots to fire
'''

class TriangleShot(object):

	def __init__(self):
		self.shotOffsets = [(-1,0), (1,-1), (0,1)]
		self.offsetsBySource = {}
		self.center = None

	def shoot(self, bots, targetPos):
		logging.info('Attempt triangle shot at %s', targetPos)
		self.offsetsBySource.clear()
		shotCount = 0
		response = []
		self.center = (targetPos.x, targetPos.y)
		for bot in bots:
			if not bot.alive:
				continue
			x = targetPos.x + self.shotOffsets[shotCount][0]
			y = targetPos.y + self.shotOffsets[shotCount][1]
			response.append(actions.Cannon(bot_id=bot.bot_id, x=x, y=y))
			self.offsetsBySource[bot.bot_id] = self.shotOffsets[shotCount]
			shotCount += 1
		return response

	def findTargets(self, events):
		targetsPos = []
		if not self.center:
			return targetsPos
		shipsHit = self._getShipsHit(events)
		for bot_id in shipsHit:
			scoringSources = self._getSourcesHittingTarget(bot_id, events)
			targetsPos += self._triangulate(scoringSources)
		self.clear()
		logging.info('Triangle shot found targets: %s', targetsPos)
		return targetsPos

	def _getShipsHit(self, events):
		shipsHit = set()
		for event in events:
			if event.event == 'hit':
				shipsHit.add(event.bot_id)
		return shipsHit

	def _getSourcesHittingTarget(self, target, events):
		scoringSources = []
		for event in events:
			if event.event == 'hit' and event.bot_id == target:
				scoringSources.append(event.source)
		return scoringSources

	def _triangulate(self, sources):
		hits = len(sources)
		if hits < 2:
			return []
		elif hits == 2:
			pos = cube_add(self.center, self.offsetsBySource[sources[0]])
			pos = cube_add(pos, self.offsetsBySource[sources[1]])
			return [messages.Pos(pos[0], pos[1])]
		elif hits == 3:
			return [messages.Pos(self.center[0], self.center[1])]

	def clear(self):
		self.offsetsBySource.clear()
		self.center = None