
from collections import deque

from tyckiting_client.notifications import defaultNotificationCenter, ID_START_ROUND_NOTIFICATION
from tyckiting_client import hexagon
from tyckiting_client.shootingField import ShootingField

STRAIGHT_DISTANCE2_PATTERN = {'stay':0, 'dist1':0, 'dist2Straight':2, 'dist2Curve':0}
BALANCED_PATTERN = {'stay':1, 'dist1':0, 'dist2Straight':2, 'dist2Curve':2}
RANDOM_MOVE_PATTERN = {'stay':1, 'dist1':1, 'dist2Straight':1, 'dist2Curve':1}
STAY_PATTERN = {'stay':1, 'dist1':0, 'dist2Straight':0, 'dist2Curve':0}

FIELD_RADIUS = 14
MOVE_RADIUS = 2
SHOOT_RADIUS = 1

class Tracker(object):

	'''
	tracks the movement enemies
	decide the target by assuming the most probable movement
	provide shoot coordiantes by maximizing the damage to 
	the enemy based on predicted movement patterns

	TODO: attention to edges and friendly ships
	'''

	def __init__(self, pattern):
		self.knownEnemyPositions = []
		self.movementCounter = pattern.copy()
		self.trackedTarget = None
		defaultNotificationCenter.registerFunc(ID_START_ROUND_NOTIFICATION, self._update)

	def getTarget(self):
		return self.trackedTarget

	def getShootCoordinates(self, amount, teamPositions=list(), target=None):
		if not target:
			target = self.getTarget()
		if not target:
			return None
		field = self._createField(target, teamPositions)
		relativeCoordinates = field.getBestCoordinates(SHOOT_RADIUS, amount)
		return [hexagon.cube_add(target, coord) for coord in relativeCoordinates]

	def _createField(self, center, teamPositions=list()):
		field = ShootingField(MOVE_RADIUS+1, totalProbability=0)
		coordinates = hexagon.getCircle(MOVE_RADIUS+1, center[0], center[1])
		coordinates = hexagon.extractValidCoordinates(coordinates, FIELD_RADIUS)
		for coord in coordinates:
			moveType = self._getMovementType(center, coord)
			relativePosition = hexagon.cube_substract(coord, center)
			if coord in teamPositions:
				value = float('-inf')
			elif moveType:
				value = self.movementCounter[moveType]
			else:
				value = 0
			field.set(relativePosition, value)
		return field

	def _update(self, notification):
		newPositions = []
		for event in notification.data['events']:
			if event.event == 'radarEcho' or event.event == 'see':
				newPositions.append(event.pos)
		self._updateCounter(newPositions)
		self.knownEnemyPositions = newPositions
		self._updateTrackedTarget(newPositions, self.trackedTarget)

	def _updateCounter(self, newPositions):
		usedPositionStart = set()
		usedPositionDestination = set()
		movePairs = self._getPossibleMovements(self.knownEnemyPositions, newPositions)
		actionsSortedByProbability = sorted(self.movementCounter, key=self.movementCounter.get, reverse=True)
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
		else:
			return None

	def _updateTrackedTarget(self, targetsPos, oldTarget):
		target = None
		if oldTarget and len(targetsPos) > 0:
			validPositions = hexagon.extractValidCoordinates(targetsPos, MOVE_RADIUS, oldTarget)
			if len(validPositions) > 0:
				target = validPositions.pop()
		if not target and len(targetsPos) > 0:
			target = targetsPos[0]
		self.trackedTarget = target

