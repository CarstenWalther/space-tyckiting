import random
import logging

from tyckiting_client import hexagon
from tyckiting_client.messages import Pos

import tyckiting_client.notifications as notifications

class Scanning(object):

	def __init__(self, config):
		self.config = config

	def getScanPosition(self):
		coords = self.getPossibleScanPositions()
		coord = random.choice(list(coords))
		return Pos(coord[0], coord[1])

	def getPossibleScanPositions(self):
		raise NotImplementedError()

class DontOvershootScanning(Scanning):

	def getPossibleScanPositions(self):
		return hexagon.getCircle(radius=self.config.field_radius-self.config.radar)


class StatisticalScanning(Scanning):

	def createField(self, radius):
		self.enemyPossibility = dict()
		total = hexagon.totalAmountOfHexagons(radius)
		for pos in hexagon.getCircle(radius):
			self.enemyPossibility[pos] = 1.0 / total

	def getNewEnemyPossibility(self, pos):
		possibleMoveOriginFields = []
		for r in range(1, self.config.move + 1):
			possibleMoveOriginFields += hexagon.get_ring(pos, r)
		possibleMoveOriginFields = hexagon.extractValidCoordinates(possibleMoveOriginFields, self.config.field_radius)

		possibilities = [self.enemyPossibility[field] for field in possibleMoveOriginFields]
		return sum(possibilities) / len(possibilities)

	def ageFieldByOneRound(self):
		newField = dict()
		for pos in hexagon.getCircle(self.config.field_radius):
			newField[pos] = self.getNewEnemyPossibility(pos)
		self.enemyPossibility = newField

	def mindOwnScans(self, notification):
		pass

	def mindEventAndBots(self, notification):
		pass


	def __init__(self, config):
		super.__init__(config)
		self.config = config
		self.createField(config.field_radius)

		notifications.defaultNotificationCenter.registerFunc(notifications.ID_END_ROUND_NOTIFICATION, self.mindOwnScans)
		notifications.defaultNotificationCenter.registerFunc(notifications.ID_START_ROUND_NOTIFICATION, self.mindEventAndBots)


	def getPossibleScanPositions(self):
		pass