import random
import logging

from tyckiting_client import hexagon
from tyckiting_client.notifications import defaultNotificationCenter
from tyckiting_client.notifications import ID_END_ROUND_NOTIFICATION
from tyckiting_client.notifications import ID_START_ROUND_NOTIFICATION
from tyckiting_client.messages import Pos
from tyckiting_client.probabilityField import ProbabilityField

from tyckiting_client.utilities import *

class Scanning(object):

	def __init__(self, config):
		self.config = config

	def getScanPosition(self):
		coords = self.getPossibleScanPositions()
		coord = random.choice(list(coords))
		return Pos(coord[0], coord[1])

	def getPossibleScanPositions(self, amount=1):
		raise NotImplementedError()


class RandomScanning(Scanning):

	def getPossibleScanPositions(self, amount=1):
		return hexagon.getCircle(radius=self.config.field_radius)


class DontOvershootScanning(Scanning):

	def getPossibleScanPositions(self, amount=1):
		return hexagon.getCircle(radius=self.config.field_radius-self.config.radar)


class StatisticalScanning(Scanning):

	def __init__(self, config):
		super(StatisticalScanning, self).__init__(config)
		self.enemyProbabilityField = ProbabilityField(config.field_radius, self.config.bots)
		defaultNotificationCenter.registerFunc(ID_END_ROUND_NOTIFICATION, self._mindOwnScans)
		defaultNotificationCenter.registerFunc(ID_START_ROUND_NOTIFICATION, self._mindEventAndBots)

	def _mindOwnScans(self, notification):
		for action in notification.data['actions']:
			if action.type == 'radar':
				self.enemyProbabilityField.clear(self.config.radar, action.x, action.y)

	@log_execution_time
	def _mindEventAndBots(self, notification):
		for bot in notification.data['bots']:
			self.enemyProbabilityField.clear(self.config.see, bot.pos.x, bot.pos.y)
		for event in notification.data['events']:
			if event.event == 'see' or event.event == 'radarEcho':
				pos = (event.pos.x, event.pos.y)
				self.enemyProbabilityField.set(pos, 1.0)
			elif event.event == 'die':
				# think about cleaning the possibilities in the area
				pass
		self.enemyProbabilityField.blur(self.config.move)

	@log_execution_time
	def getPossibleScanPositions(self, amount=1):
		coordinates = self.enemyProbabilityField.getBestCoordinates(self.config.radar, amount)
		return [Pos(*coord) for coord in coordinates]