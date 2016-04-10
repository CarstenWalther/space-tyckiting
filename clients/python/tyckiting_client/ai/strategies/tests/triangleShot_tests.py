import unittest

from tyckiting_client.ai.strategies.triangleShot import TriangleShot
from tyckiting_client.messages import Pos, Bot, Event

class TriangleShotTest(unittest.TestCase):

	def setUp(self):
		self.triShot = TriangleShot()
		self.bots = [
			Bot(0, 'bot1', 1, True, {"x":-13,"y":5}, 10),
			Bot(1, 'bot2', 1, True, {"x":-10,"y":7}, 10),
			Bot(2, 'bot3', 1, True, {"x":  9,"y":2}, 10),
		]

	def test_shoot(self):
		position = Pos(1, 1) 
		response = self.triShot.shoot(self.bots, position)
		expectedTargets = [set([(2,0), (1,2), (0,1)]), set([(1,0), (0,2), (2,1)])]
		targets = set()
		for action in response:
			targets.add((action.x, action.y))
		self.assertTrue(targets == expectedTargets[0] or targets == expectedTargets[1])

	def test_findTargets_one_target(self):
		position = Pos(-10, -3)
		self.triShot.center = (position.x, position.y)
		self.triShot.offsetsBySource = {0: (-1,0), 1: (1,-1), 2:(0,1)}
		events = [
			Event('hit', source=0, botId=4),
			Event('hit', source=2, botId=4)
		]
		targets = self.triShot.findTargets(events)
		expectedTarget = Pos(-11, -2)
		self.assertEquals(len(targets), 1)
		self.assertEquals(targets[0], expectedTarget)