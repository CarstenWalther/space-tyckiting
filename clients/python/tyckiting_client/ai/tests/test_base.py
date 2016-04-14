import unittest
import json

from tyckiting_client.ai import base
from tyckiting_client import messages

class BaseTest(unittest.TestCase):

	def test_getEndangeredBots_bot_sees_but_is_dead(self):
		data = json.loads('[{"event":"move","botId":5,"pos":{"x":2,"y":-4}},{"event":"hit","source":4,"botId":5}, \
			{"event":"damaged","botId":5,"damage":1},{"event":"see","source":5,"botId":0,"pos":{"x":2,"y":-3}}, \
			{"event":"die","botId":5}]')
		events = list(map(lambda e: messages.Event(**e), data or []))
		ai = base.BaseAi(messages.Config())
		endangeredBots = ai.getEndangeredBots(events)
		expectedEndangeredBots = set()
		self.assertEqual(endangeredBots, expectedEndangeredBots)

	def test_addIfNotDead_bot_is_dead(self):
		data = json.loads('[{"event":"move","botId":5,"pos":{"x":2,"y":-4}},{"event":"hit","source":4,"botId":5}, \
			{"event":"damaged","botId":5,"damage":1},{"event":"see","source":5,"botId":0,"pos":{"x":2,"y":-3}}, \
			{"event":"die","botId":5}]')
		events = list(map(lambda e: messages.Event(**e), data or []))
		endangeredBots = set()
		ai = base.BaseAi(messages.Config())
		ai.addIfNotDead(endangeredBots, 5, events)
		expectedEndangeredBots = set()
		self.assertEqual(endangeredBots, expectedEndangeredBots)

	def test_addIfNotDead_bot_is_dead(self):
		data = json.loads('[{"event":"move","botId":5,"pos":{"x":2,"y":-4}},{"event":"hit","source":4,"botId":5}, \
			{"event":"damaged","botId":5,"damage":1},{"event":"see","source":5,"botId":0,"pos":{"x":2,"y":-3}}]')
		events = list(map(lambda e: messages.Event(**e), data or []))
		endangeredBots = set()
		ai = base.BaseAi(messages.Config())
		ai.addIfNotDead(endangeredBots, 5, events)
		expectedEndangeredBots = set([5])
		self.assertEqual(endangeredBots, expectedEndangeredBots)