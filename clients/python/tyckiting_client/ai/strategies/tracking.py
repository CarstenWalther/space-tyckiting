
from collections import deque

from tyckiting_client.notifications import defaultNotificationCenter, ID_START_ROUND_NOTIFICATION
from tyckiting_client import hexagon

STRAIGHT_DISTANCE2_PATTERN = {'stay':0, 'dist1':0, 'dist2Straight':2, 'dist2Curve':0}
BALANCED_PATTERN = {'stay':1, 'dist1':0, 'dist2Straight':2, 'dist2Curve':2}
MOVE_RADIUS = 2

class Tracker(object):

	'''
	tracks the movement enemies
	decide the target by assuming the most probable movement
	provide shoot coordiantes by maximizing the damage to 
	the enemy based on predicted movement patterns

	TODO: take edges into account
	'''

	def __init__(self, pattern):
		self.knownEnemyPositions = []
		self.movementCounter = pattern.copy()
		self.trackedTarget = None
		defaultNotificationCenter.registerFunc(ID_START_ROUND_NOTIFICATION, self._update)

	def getTarget(self):
		return self.trackedTarget

	def getShootCoordinates(self, amount):
		pass

	def _update(self, notification):
		newPositions = []
		if not self.teamBots:
			initTeamBots(notification.data['bots'])
		for event in notification.data['events']:
			if event.event == 'radarEcho' or event.event == 'see':
				newPositions.append(event.pos)
		self._updateCounter(newPositions)
		self.knownEnemyPositions = newPositions
		self._determineTrackedTarget(newPositions, self.trackedTarget)

	def _updateCounter(self, newPositions):
		usedPositionStart = set()
		usedPositionDestination = set()
		movePairs = self._getPossibleMovements(self.knownEnemyPositions, newPositions)
		actionsSortedByProbability = sorted(self.movementCounter, key=self.movementCounter.get, reverse=True)
		print(actionsSortedByProbability)
		for action in actionsSortedByProbability:
			for movePair in movePairs:
				if movePair[0] not in usedPositionStart and \
					movePair[1] not in usedPositionDestination:
					moveType = self._getMovementType(movePair[0], movePair[1])
					if moveType == action:
						self.movementCounter[moveType] += 1
						usedPositionStart.add(movePair[0])
						usedPositionDestination.add(movePair[1])

	def _getPossibleMovements(self, oldPositions, newPositions):
		movePairs = deque()
		for oldPos in oldPositions:
			for newPos in newPositions:
				if hexagon.distance(oldPos, newPos) <= MOVE_RADIUS:
					movePairs.append((oldPos, newPos))
		return movePairs

	def _getMovementType(self, start, destination):
		distance = hexagon.distance(start, destination)
		if distance == 0:
			return 'stay'
		elif distance == 1:
			return 'dist1'
		elif distance == 2:
			if hexagon.isStraightLine(start, destination):
				return 'dist2Straight'
			else:
				return 'dist2Curve'

	def _determineTrackedTarget(self, targetsPos, center):
		if len(targetsPos) == 0:
			return None
		if center
			validPositions = hexagon.extractValidCoordinates(targetsPos, self.config.move, center)
			if len(validPositions) > 0:
				return validPositions.pop()
		else:
			return targetsPos.pop()


