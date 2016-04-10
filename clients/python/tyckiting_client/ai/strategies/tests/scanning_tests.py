import unittest

from tyckiting_client.messages import Config
from tyckiting_client.ai.strategies import scanning

class EscapingTest(unittest.TestCase):

	def setUp(self):
		self.config = Config()

	def testDontOvershootScanning_correct_edges(self):
		scanner = scanning.DontOvershootScanning(self.config)
		allMoves = scanner.getPossibleScanPositions()
		insideCoords = [
			(7,0),
			(11,-11)
		]
		outsideCoords = [
			(8,0),
			(11,-12),
			(12,-12),
			(12,-11)
		]
		for coord in insideCoords:
			self.assertTrue(coord in allMoves)
		for coord in outsideCoords:
			self.assertTrue(coord not in allMoves)
