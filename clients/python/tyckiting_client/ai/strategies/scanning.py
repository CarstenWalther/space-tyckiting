import random
import logging

from tyckiting_client import hexagon
from tyckiting_client import actions
from tyckiting_client import notifications
from tyckiting_client.messages import Pos


class Scanning(object):

	def __init__(self, config):
		self.config = config

	def getScanPosition(self):
		coords = self.getPossibleScanPositions()
		coord = random.choice(list(coords))
		return Pos(coord[0], coord[1])

	def getPossibleScanPositions(self):
		raise NotImplementedError()

class RandomScanning(Scanning):

	def getPossibleScanPositions(self):
		return hexagon.getCircle(radius=self.config.field_radius)

class DontOvershootScanning(Scanning):

	def getPossibleScanPositions(self):
		return hexagon.getCircle(radius=self.config.field_radius-self.config.radar)


class StatisticalScanning(Scanning):

	def __init__(self, config):
		super(StatisticalScanning, self).__init__(config)
		self.createField(config.field_radius)

		notifications.defaultNotificationCenter.registerFunc(notifications.ID_END_ROUND_NOTIFICATION, self.mindOwnScans)
		notifications.defaultNotificationCenter.registerFunc(notifications.ID_START_ROUND_NOTIFICATION, self.mindEventAndBots)

	def createField(self, radius):
		self.enemyPossibility = dict()
		total = hexagon.totalAmountOfHexagons(radius)
		for pos in hexagon.getCircle(radius):
			self.enemyPossibility[pos] = self.config.bots / total

	def getNewEnemyPossibility(self, pos):
		possibleMoveOriginFields = hexagon.getCircle(self.config.move, pos[0], pos[1])
		possibleMoveOriginFields = hexagon.extractValidCoordinates(possibleMoveOriginFields, self.config.field_radius)

		possibilities = [self.enemyPossibility[field] for field in possibleMoveOriginFields]
		return sum(possibilities) / len(possibilities)

	def ageFieldByOneRound(self):
		newField = dict()
		for pos in hexagon.getCircle(self.config.field_radius):
			newField[pos] = self.getNewEnemyPossibility(pos)
		self.enemyPossibility = newField

	def mindOwnScans(self, notification):
		actionList = notification.data['actions']
		for action in actionList:
			if action.type == 'radar':
				fields = hexagon.getCircle(self.config.radar, action.x, action.y)
				fields = hexagon.extractValidCoordinates(fields, self.config.field_radius)
				for field in fields:
					self.enemyPossibility[field] = 0.0

	def mindEventAndBots(self, notification):
		bots = notification.data['bots']
		events = notification.data['events']

		for event in events:
			if event.event == 'see' or event.event == 'radarEcho':
				pos = (event.pos.x, event.pos.y)
				self.enemyPossibility[pos] = 1.0

		self.ageFieldByOneRound()

	def getPossibleScanPositions(self):
		pass