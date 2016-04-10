import unittest

from tyckiting_client.messages import Pos, Bot, Config
from tyckiting_client.ai.strategies import escaping

class EscapingTest(unittest.TestCase):

	def setUp(self):
		self.config = Config()
		self.bot = Bot(0, 'bot1', 1, True, {"x":2,"y":1}, 10)

	def testStraightdistance2Escaping(self):
		movement = escaping.StraightDistance2Escaping(self.config)
		allMoves = set(movement.getPossibleMoves(self.bot))
		expectedMoves = set((
			Pos(x=0, y=1),
			Pos(x=2, y=-1),
			Pos(x=4, y=-1),
			Pos(x=4, y=1),
			Pos(x=2, y=3),
			Pos(x=0, y=3),
		))
		self.assertEqual(allMoves, expectedMoves)
