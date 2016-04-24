
from collections import deque

from tyckiting_client.notifications import defaultNotificationCenter
from tyckiting_client.notifications import ID_START_ROUND_NOTIFICATION
from tyckiting_client.notifications import ID_END_ROUND_NOTIFICATION
from tyckiting_client import hexagon
from tyckiting_client.shootingField import ShootingField

STRAIGHT_DISTANCE2_PATTERN = {'stay':0, 'dist1':0, 'dist2Straight':2, 'dist2Curve':0}
BALANCED_PATTERN = {'stay':1, 'dist1':0, 'dist2Straight':2, 'dist2Curve':2}
RANDOM_MOVE_PATTERN = {'stay':1, 'dist1':1, 'dist2Straight':1, 'dist2Curve':1}
STAY_PATTERN = {'stay':1, 'dist1':0, 'dist2Straight':0, 'dist2Curve':0}

FIELD_RADIUS = 14
MOVE_RADIUS = 2
SHOOT_RADIUS = 1

class UncertainTracker(object):

	'''
	Similar to the standard tracking but also tracks enemies being hit.
	Such enemies can be tracked with an uncertainity of radius 1.
	Less scanning is needed but it is harder to hit the enemies.
	Is it all worth it??? We will see

	prefer certain targets over uncertain targets
	'''

	def __init__(self, pattern):
		self.knownEnemyPositions = []
		self.knownUncertainEnemyPositions = []
		self.shootCoordByBotId = {}
		self.movementCounter = pattern.copy()
		self.trackedTarget = None
		defaultNotificationCenter.registerFunc(ID_START_ROUND_NOTIFICATION, self._updateEvents)
		defaultNotificationCenter.registerFunc(ID_END_ROUND_NOTIFICATION, self._updateActions)

	def getTarget(self):
		#consists of (x, y, radius)
		return self.trackedTarget

	def getShootCoordinates(self, amount, teamPositions=list()):
		if not self.trackedTarget:
			return None
		targetCoord = self.trackedTarget[0:2]
		certainRadius = self.trackedTarget[2]
		field = self._createField(targetCoord, teamPositions, certainRadius)
		relativeCoordinates = field.getBestCoordinates(SHOOT_RADIUS, amount)
		return [hexagon.cube_add(targetCoord, coord) for coord in relativeCoordinates]

	def _createField(self, center, teamPositions=list(), certainRadius=0):
		if certainRadius == 0:
			return self._fillCertainField(center, teamPositions)
		elif certainRadius == 1:
			return self._fillUncertainField(center, teamPositions)

	def _fillCertainField(self, center, teamPositions):
		radius = MOVE_RADIUS + 1
		field = ShootingField(radius, totalProbability=0)
		coordinates = hexagon.getCircle(radius, center[0], center[1])
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

	def _fillUncertainField(self, center, teamPositions):
		radius = MOVE_RADIUS + 2
		typeProbabilities = self._generateTypeProbabilities()
		field = ShootingField(radius, totalProbability=0)
		coordinates = hexagon.getCircle(radius, center[0], center[1])
		coordinates = hexagon.extractValidCoordinates(coordinates, FIELD_RADIUS)
		sourceFields = hexagon.getCircle(MOVE_RADIUS, center[0], center[1])
		sourceFields = hexagon.extractValidCoordinates(coordinates, FIELD_RADIUS)
		for coord in coordinates:
			relativePosition = hexagon.cube_substract(coord, center)
			if coord in teamPositions:
				field.set(relativePosition, float('-inf'))
			else:
				for sourceCoord in sourceFields:
					moveType = self._getMovementType(coord, sourceCoord)
					if moveType:
						value = field.field[relativePosition]
						value += typeProbabilities[moveType]
						field.set(relativePosition, value)
		return field

	def _generateTypeProbabilities(self):
		total = sum(self.movementCounter.values())
		typesByProb = {}
		for key in self.movementCounter:
			typesByProb[key] = self.movementCounter[key] / total
		return typesByProb

	def _updateActions(self, notification):
		self.shootCoordByBotId = {}
		for action in notification.data['actions']:
			if action.type == 'cannon':
				self.shootCoordByBotId[action.bot_id] = (action.x, action.y)

	def _updateEvents(self, notification):
		certainPositions = self._findCertainPositions(notification)
		self._updateCounter(self.knownEnemyPositions, certainPositions)
		self.knownEnemyPositions = certainPositions
		self.knownUncertainEnemyPositions = self._findUncertainPositions(notification, certainPositions)		
		self._updateTrackedTarget()

	def _findCertainPositions(self, notification):
		positions = []
		for event in notification.data['events']:
			if event.event == 'radarEcho' or event.event == 'see':
				positions.append(event.pos)
		return positions

	def _findUncertainPositions(self, notification, certainPositions):
		positions = []
		for event in notification.data['events']:
			if event.event == 'hit':
				botId = event.source
				positions.append(self.shootCoordByBotId[botId])
		return positions

	def _updateCounter(self, oldPositions, newPositions):
		usedPositionStart = set()
		usedPositionDestination = set()
		movePairs = self._getPossibleMovements(oldPositions, newPositions)
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

	def _updateTrackedTarget(self):
		target = self._getCertainTarget()
		if not target:
			target = self._getUncertainTarget()
		self.trackedTarget = target

	def _getCertainTarget(self):
		target = None
		if self.trackedTarget and len(self.knownEnemyPositions) > 0:
			validPositions = hexagon.extractValidCoordinates(
				self.knownEnemyPositions,
				MOVE_RADIUS + self.trackedTarget[2],
				self.trackedTarget[0:2])
			if len(validPositions) > 0:
				target = validPositions.pop()
		if not target and len(self.knownEnemyPositions) > 0:
			target = self.knownEnemyPositions[0]
		if target:
			return (target[0], target[1], 0)
		else:
			return None

	def _getUncertainTarget(self):
		for coord in self.knownUncertainEnemyPositions:
			if hexagon.distance(self.trackedTarget[0:2], coord) <= MOVE_RADIUS + 1:
				return (coord[0], coord[1], 1)
		if len(self.knownUncertainEnemyPositions) > 1:
			coord = self.knownUncertainEnemyPositions[0]
			return (coord[0], coord[1], 1)
		return None


