import random
import logging

from tyckiting_client import hexagon
from tyckiting_client.messages import Pos

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