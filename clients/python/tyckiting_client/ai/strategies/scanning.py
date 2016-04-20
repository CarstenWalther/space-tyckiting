import random
import logging

from tyckiting_client import hexagon
from tyckiting_client.messages import Pos
from tyckiting_client.gameField import GameField

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
		self.gameField = GameField(config)

	@log_execution_time
	def getPossibleScanPositions(self, amount=1):
		coordinates = self.gameField.enemyProbabilityField.getBestCoordinates(self.config.radar, amount)
		return [Pos(*coord) for coord in coordinates]