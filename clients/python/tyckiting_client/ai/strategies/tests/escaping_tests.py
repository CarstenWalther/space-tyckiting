import unittest

from tyckiting_client.messages import Bot, Config
from tyckiting_client.ai.strategies import escaping

class EscapingTest(unittest.TestCase):

	def setUp(self):
		self.config = Config()
		self.bot = Bot(0, 'bot1', 1, True, {"x":2,"y":1}, 10)

	def testStraightdistance2Escaping(self):
		movement = escaping.StraightDistance2Escaping(self.config)
		allMoves = set(movement.getPossibleMoves(self.bot))
		expectedMoves = set((
			(0, 1),
			(2,-1),
			(4, 1),
			(4,-1),
			(2, 3),
			(0, 3),
		))
		self.assertEqual(allMoves, expectedMoves)

	def test_RandomEscaping_getPossibleMoves_center(self):
		movement = escaping.RandomEscaping(self.config)
		bot = Bot(1, 'bot1', '1', pos={'x':0, 'y':0})
		positions = set(movement.getPossibleMoves(bot))
		expected_positions = set([
			(-2, 0),
			(-2, 1),
			(-2, 2),
			(-1,-1),
			(-1, 0),
			(-1, 1),
			(-1, 2),
			( 0,-2),
			( 0,-1),
			( 0, 1),
			( 0, 2),
			( 1,-2),
			( 1,-1),
			( 1, 0),
			( 1, 1),
			( 2,-2),
			( 2,-1),
			( 2, 0),
		])
		self.assertEqual(positions, expected_positions)

	def test_RandomEscaping_getPossibleMoves_edge(self):
		movement = escaping.RandomEscaping(self.config)
		bot = Bot(1, 'bot1', '1', pos={'x':14, 'y':0})
		positions = set(movement.getPossibleMoves(bot))
		expected_positions = set([
			(12, 0),
			(12, 1),
			(12, 2),
			(13,-1),
			(13, 0),
			(13, 1),
			(14,-2),
			(14,-1),
		])
		self.assertEqual(positions, expected_positions)

	def testAvoidSelfhit(self):
		enemy_pos = [2, -1]

		movement = escaping.AvoidSelfhit(self.config)
		movement.setEnemy(enemy_pos)

		allMoves = set(movement.getPossibleMoves(self.bot))
		expectedMoves = set((
			(4, 1),
			(2, 3),
			(0, 3),
		))
		self.assertEqual(allMoves, expectedMoves)