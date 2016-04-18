import unittest

from tyckiting_client.probabilityField import ProbabilityField

class ProbabilityFieldTest(unittest.TestCase):

	def test_getBestCoordinates_one_enemy_one_blur(self):
		field = ProbabilityField(radius=14, totalProbability=0)
		field.set((1,1), 1)
		field.blur(radius=3)
		result = field.getBestCoordinates(radius=3, amount=1)
		expectedResult = [(1,1)]
		self.assertEqual(result, expectedResult)

	def test_getBestCoordinates_one_enemy_one_blur_2(self):
		field = ProbabilityField(radius=14, totalProbability=0)
		field.set((11,0), 1)
		field.blur(radius=3)
		result = field.getBestCoordinates(radius=3, amount=1)
		expectedResult = [(11,0)]
		self.assertEqual(result, expectedResult)
