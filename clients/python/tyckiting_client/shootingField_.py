import random

import numpy as np
from tyckiting_client import hexagon
from tyckiting_client.probabilityField import ProbabilityField

DAMPING_FACTOR = 0.5

class ShootingField(ProbabilityField):

	def getBestCoordinates(self, radius, amount=1):
		result = []
		tmpField = np.ones_like(self.field) * self.field

		while len(result) < amount:
			blurredTmpField = self._combsum(tmpField, radius)
			blurredTmpField += tmpField

			ind = np.where(blurredTmpField == blurredTmpField.max())
			pos = random.choice(np.transpose(ind))
			result.append((pos[0], pos[1]))

			# reset this spot
			coords = self._filterValid( self._translateIntoField( self._getCircle(radius, pos[0], pos[1]) ) )
			tmpField[ coords[:,0], coords[:,1] ] *= 0.5
			
		return result