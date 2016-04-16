import random
import logging
import heapq

# debug
import scipy.misc
import math
import numpy as np

from tyckiting_client import hexagon
from tyckiting_client import actions
from tyckiting_client import notifications
from tyckiting_client.messages import Pos

from tyckiting_client.utilities import *

class Scanning(object):

	def __init__(self, config):
		self.config = config

	def getScanPosition(self, amount=1):
		coords = self.getPossibleScanPositions(amount)
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
		self.createField(config.field_radius)

		notifications.defaultNotificationCenter.registerFunc(notifications.ID_END_ROUND_NOTIFICATION, self.mindOwnScans)
		notifications.defaultNotificationCenter.registerFunc(notifications.ID_START_ROUND_NOTIFICATION, self.mindEventAndBots)

	def createField(self, radius):
		self.enemyPossibility = dict()
		total = hexagon.totalAmountOfHexagons(radius)
		for pos in hexagon.getCircle(radius):
			self.enemyPossibility[pos] = self.config.bots / total

		#self.img_count = 0
		#self.outputFieldAsImage(self.enemyPossibility)

	def getNewEnemyPossibility(self, pos):
		possibleMoveOriginFields = hexagon.getCircle(self.config.move, pos[0], pos[1])
		possibleMoveOriginFields = hexagon.extractValidCoordinates(possibleMoveOriginFields, self.config.field_radius)

		possibilities = [self.enemyPossibility[field] for field in possibleMoveOriginFields]
		return sum(possibilities) / len(possibilities)

	def outputFieldAsImage(self, field):
		filename = 'statfield_{:03d}.png'.format(self.img_count)
		self.img_count += 1
		dimension = self.config.field_radius * 2
		
		img = np.zeros((dimension + 2, dimension + 2))
		for pos in field.keys():
			x, y = pos
			img[int(x+dimension/2), int(y+dimension/2)] = field[pos]

		scipy.misc.toimage(img).save(filename)

	@log_execution_time
	def ageFieldByOneRound(self):
		newField = dict()
		for pos in hexagon.getCircle(self.config.field_radius):
			newField[pos] = self.getNewEnemyPossibility(pos)
		self.enemyPossibility = newField
		#self.outputFieldAsImage(newField)

	def mindOwnScans(self, notification):
		actionList = notification.data['actions']
		for action in actionList:
			if action.type == 'radar':
				fields = hexagon.getCircle(self.config.radar, action.x, action.y)
				for field in fields:
					if field in self.enemyPossibility:
						self.enemyPossibility[field] = 0.0

	def mindEventAndBots(self, notification):
		bots = notification.data['bots']
		events = notification.data['events']

		for bot in bots:
			fields = hexagon.getCircle(self.config.see, bot.pos.x, bot.pos.y)
			for field in fields:
				if field in self.enemyPossibility:
					self.enemyPossibility[field] = 0.0

		for event in events:
			if event.event == 'see' or event.event == 'radarEcho':
				pos = (event.pos.x, event.pos.y)
				self.enemyPossibility[pos] = 1.0
			elif event.event == 'die':
				# think about cleaning the possibilities in the area
				pass

		self.ageFieldByOneRound()

	def getScanPosition(self, amount=1):
		return self.getPossibleScanPositions(amount)[0]

	@log_execution_time
	def getPossibleScanPositions(self, amount=1):
		positions = []
		# min heap
		totalTiles = set(hexagon.getCircle(self.config.field_radius))
		usedTiles = set()

		while len(positions) < amount:
			bestPosition = None
			bestPositionScore = -1

			for pos in random.sample(totalTiles, int(len(totalTiles)/5)):
				fields = hexagon.getCircle(self.config.radar, pos[0], pos[1])
				fields = set(hexagon.extractValidCoordinates(fields, self.config.field_radius))
				fields = fields - usedTiles
				
				findProbability = sum([self.enemyPossibility[field] for field in fields])
				if findProbability > bestPositionScore:
					bestPosition = pos
					bestPositionScore = findProbability
			
			positions.append(Pos(*bestPosition))
			usedTiles |= set(hexagon.getCircle(self.config.radar, bestPosition[0], bestPosition[1]))

		return positions
