import random

from tyckiting_client import hexagon
from tyckiting_client.probabilityField import ProbabilityField

class ShootingField(ProbabilityField):

	def getBestCoordinates(self, radius, amount=1):
		result = []
		allCoordinates = list(hexagon.getCircle(self.fieldRadius))
		random.shuffle(allCoordinates)
		usedCoordinates = set()

		while len(result) < amount:
			bestPosition = None
			bestPositionScore = -1

			for coord in allCoordinates:
				positions = hexagon.getCircle(radius, coord[0], coord[1])
				positions = hexagon.extractValidCoordinates(positions, self.fieldRadius)
				
				totalProbability = sum(self.field[position] for position in positions)
				for position in usedCoordinates:
					if position in positions:
						totalProbability -= self.field[position]/2
				totalProbability += self.field[coord]
				if totalProbability > bestPositionScore:
					bestPosition = coord
					bestPositionScore = totalProbability
			
			result.append(bestPosition)
			newUsedCoordinates = hexagon.getCircle(radius, bestPosition[0], bestPosition[1])
			newUsedCoordinates = hexagon.extractValidCoordinates(newUsedCoordinates, self.fieldRadius)
			usedCoordinates |= newUsedCoordinates

		return result