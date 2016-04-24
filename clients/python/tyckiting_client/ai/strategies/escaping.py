import random
import logging

import numpy as np

from tyckiting_client import hexagon
from tyckiting_client.messages import Pos

from tyckiting_client.notifications import defaultNotificationCenter
from tyckiting_client.notifications import ID_START_ROUND_NOTIFICATION
from tyckiting_client.gameField import GameField

class Escaping(object):

	def __init__(self, config):
		self.config = config

	def getMove(self, bot):
		coords = self.getPossibleMoves(bot)
		coord = random.choice(list(coords))
		pos = Pos(coord[0], coord[1])
		logging.info('Move %d from %s to %s', bot.bot_id, bot.pos, pos)
		return pos

	def getPossibleMoves(self, bot):
		raise NotImplementedError()

class RandomEscaping(Escaping):

	def getPossibleMoves(self, bot):
		coordinates = set()
		for radius in range(1, self.config.move + 1):
			coordinates |= hexagon.get_ring((bot.pos.x, bot.pos.y), radius)
		coordinates = hexagon.extractValidCoordinates(coordinates, self.config.field_radius)
		return coordinates

class StraightDistance2Escaping(Escaping):

	def getPossibleMoves(self, bot):
		coordinates = set()
		center = (bot.pos.x, bot.pos.y)
		for direction in range(6):
			coord = hexagon.neighbor(center, direction)
			coord = hexagon.neighbor(coord, direction)
			coordinates.add(coord)
		coordinates = hexagon.extractValidCoordinates(coordinates, self.config.field_radius)
		return coordinates

class Distance1Escaping(Escaping):

	def getPossibleMoves(self, bot):
		coordinates = set()
		center = (bot.pos.x, bot.pos.y)
		for direction in range(6):
			coord = hexagon.neighbor(center, direction)
			coordinates.add(coord)
		coordinates = hexagon.extractValidCoordinates(coordinates, self.config.field_radius)
		return coordinates

class CurvedDistance2Escaping(Escaping):

	def getPossibleMoves(self, bot):
		coordinates = set()
		center = (bot.pos.x, bot.pos.y)
		for direction in range(6):
			coord = hexagon.neighbor(center, direction)
			coord = hexagon.neighbor(coord, (direction - 1) % 6)
			coordinates.add(coord)
		coordinates = hexagon.extractValidCoordinates(coordinates, self.config.field_radius)
		return coordinates

class AvoidSelfhit(Escaping):

	def setEnemy(self, enemy_pos):
		self.enemy_pos = enemy_pos

	def getPossibleMoves(self, bot):
		logging.info('AvoidSelfhit on bot %d from enemy in %s', bot.bot_id, self.enemy_pos)
		coordinates = set()
		center = (bot.pos.x, bot.pos.y)
		max_distance = 0

		for direction in range(6):
			coord = hexagon.neighbor(center, direction)
			coord = hexagon.neighbor(coord, direction)
			distance = hexagon.distance(coord, self.enemy_pos)

			if distance == max_distance:
				coordinates.add(coord)

			elif distance > max_distance:
				coordinates.clear()
				coordinates.add(coord)
				max_distance = distance

		coordinates = hexagon.extractValidCoordinates(coordinates, self.config.field_radius)
		return coordinates

class AvoidGrouping(Escaping):

	def __init__(self, config):
		self.config = config
		self.straight = StraightDistance2Escaping(self.config)
		self.curved = CurvedDistance2Escaping(self.config)
		self.teammates = None

	def setTeammates(self, bots):
		self.teammates = bots

	def getPossibleMoves(self, bot):
		coordinates = set()
		max_distance = 0

		c1 = self.straight.getPossibleMoves(bot)
		c2 = self.curved.getPossibleMoves(bot)
		moves = c1 | c2
		distances = {}

		max_distance = 0
		for m in moves:
			distance_to_team = 32
			for own_bot in self.teammates:
				if hexagon.distance(own_bot.pos, m) < distance_to_team:
					distance_to_team = hexagon.distance(own_bot.pos, m)
			distances[m] = distance_to_team
			if distance_to_team > max_distance:
				coordinates = set()
				coordinates.add(m)
				max_distance = distance_to_team
			elif distance_to_team == max_distance:
				coordinates.add(m)

		return coordinates


class PretendToBeDead(Escaping):

	def getPossibleMoves(self, bot):
		return [(bot.pos.x, bot.pos.y)]

# The following strategies return a sorted list with possible targetFields
# starting with its proposed best target

class RunFromEnemy(Escaping):

	def getPossibleMoves(self, bot):
		coordinates = hexagon.getCircle(self.config.move, bot.pos.x, bot.pos.y)
		gameField = GameField(self.config)
		posAndEnemyProb = sorted([(gameField.enemyProbability(c), c) for c in coordinates])
		return list(zip(*posAndEnemyProb))[1]


class ChaseEnemy(Escaping):

	def getPossibleMoves(self, bot):
		coordinates = hexagon.getCircle(self.config.move, bot.pos.x, bot.pos.y)
		gameField = GameField(self.config)
		posAndEnemyProb = sorted([(gameField.enemyProbability(c), c) for c in coordinates], reverse=True)
		return list(zip(*posAndEnemyProb))[1]


class AvoidWalls(Escaping):

	def getPossibleMoves(self, bot):
		coordinates = hexagon.getCircle(self.config.move, bot.pos.x, bot.pos.y)
		posAndEnemyProb = sorted([(hexagon.distance(c, (0, 0)), c) for c in coordinates], reverse=True)
		return list(zip(*posAndEnemyProb))[1]


class AvoidWallsAdvanced(Escaping):

	def __init__(self, config):
		self.config = config
		self.straight = StraightDistance2Escaping(self.config)
		self.curved = CurvedDistance2Escaping(self.config)

	def getPossibleMoves(self, bot):
		c1 = self.straight.getPossibleMoves(bot)
		c2 = self.curved.getPossibleMoves(bot)
		moves = c1 | c2

		coordinates = set()
		for c in moves:
			if hexagon.distance(c, (0,0)) <= 12:
				coordinates.add(c)
		return coordinates


class SpreadOwnBots(Escaping):

	def __init__(self, config):
		self.config = config
		defaultNotificationCenter.registerFunc(ID_START_ROUND_NOTIFICATION, self.updateOwnBotPositions)
		self.bots = []

	def distanceToWall(self, pos):
		x = pos[0]
		y = pos[1]
		z = -x-y

		ring = max(abs(x), abs(y), abs(z))
		return self.config.field_radius - ring

	def updateOwnBotPositions(self, notification):
		self.bots = notification.data['bots']

	def getPossibleMoves(self, bot):
		coordinates = hexagon.get_ring(coords=(bot.pos.x, bot.pos.y), radius=self.config.move )
		coordinates = list(hexagon.extractValidCoordinates(coordinates,self.config.field_radius))
		
		table = np.zeros((len(coordinates), 3))
		for i, coordinate in enumerate(coordinates):
			distToMid = hexagon.distance(coordinate, (0,0))
			distToMid /= self.config.field_radius
			distToInnerCircle = 16 * (distToMid - 0.5)**4

			gameField = GameField(self.config)
			enemyProbability = gameField.enemyProbability(coordinate)

			distToClosestTeamMate = min([hexagon.distance( (b.pos.x,b.pos.y), (bot.pos.x, bot.pos.y) ) for b in self.bots if b.bot_id != bot.bot_id])
			distToClosestTeamMate /= self.config.field_radius

			table[i,:] = np.array([distToInnerCircle, enemyProbability, distToClosestTeamMate])

		table[:,1] = table[:,1] / table[:,1].sum()
		scores = table[:,0] + 1-table[:,1] + 1-table[:,2]
		return [coordinates[scores.argmin()]]
		