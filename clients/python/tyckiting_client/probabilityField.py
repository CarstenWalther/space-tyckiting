
from tyckiting_client import hexagon

class ProbabilityField(object):

	def __init__(self, radius, totalProbability=1):
		self.field = dict()
		self.totalProbability = totalProbability
		self.fieldRadius = radius
		self._initializeField(radius, totalProbability)

	def _initializeField(self, radius, totalProbability):
		fieldAmount = hexagon.totalAmountOfHexagons(radius)
		for pos in hexagon.getCircle(radius):
			self.field[pos] = totalProbability / fieldAmount

	def getBestCoordinates(self, radius, amount=1):
		result = []
		allCoordinates = set(hexagon.getCircle(self.fieldRadius))
		usedCoordinates = set()

		while len(result) < amount:
			bestPosition = None
			bestPositionScore = -1

			for coord in allCoordinates:
				positions = hexagon.getCircle(radius, coord[0], coord[1])
				positions = hexagon.extractValidCoordinates(positions, self.fieldRadius)
				positions = positions - usedCoordinates
				
				totalProbability = sum(self.field[position] for position in positions)
				if totalProbability > bestPositionScore:
					bestPosition = coord
					bestPositionScore = totalProbability
			
			result.append(bestPosition)
			usedCoordinates |= set(hexagon.getCircle(radius, bestPosition[0], bestPosition[1]))

		return result


	def clear(self, radius=None, x=0, y=0):
		if not radius:
			radius = self.fieldRadius
		positions = hexagon.getCircle(radius, x, y)
		for position in positions:
			if position in self.field:
				self.field[position] = 0.0

	def set(self, key, value):
		self.field[key] = value

	def get(self, key):
		if not key in self.field:
			return 0.0
		return self.field[key]

	def blur(self, radius):
		newField = dict()
		for pos in hexagon.getCircle(self.fieldRadius):
			newField[pos] = self._getBlurSum(pos, radius)
		self.field = newField

	def _getBlurSum(self, pos, radius):
		possibleMoveOriginFields = hexagon.getCircle(radius, pos[0], pos[1])
		possibleMoveOriginFields = hexagon.extractValidCoordinates(possibleMoveOriginFields, self.fieldRadius)
		possibilitySum = sum(self.field[position] for position in possibleMoveOriginFields)
		return possibilitySum / len(possibleMoveOriginFields)
