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
