import random
import logging

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


class PretendToBeDead(Escaping):

	def getPossibleMoves(self, bot):
		return [(bot.pos.x, bot.pos.y)]

# The following strategies return a sorted list with possible targetFields
# starting with its proposed best target

class RunFromEnemy(Escaping):

	def getPossibleMoves(self, bot):
		coordinates = hexagon.getCircle(self.config.move, bot.pos.x, bot.pos.y)
		gameField = GameField(self.config)
		logging.info('run from enemy')
		posAndEnemyProb = sorted([(gameField.enemyProbability(c), c) for c in coordinates])
		return list(zip(*posAndEnemyProb))[1]


class ChaseEnemy(Escaping):

	def getPossibleMoves(self, bot):
		coordinates = hexagon.getCircle(self.config.move, bot.pos.x, bot.pos.y)
		gameField = GameField(self.config)
		logging.info('chase enemy: ')
		posAndEnemyProb = sorted([(gameField.enemyProbability(c), c) for c in coordinates], reverse=True)
		return list(zip(*posAndEnemyProb))[1]


class AvoidWalls(Escaping):

	def getPossibleMoves(self, bot):
		coordinates = hexagon.getCircle(self.config.move, bot.pos.x, bot.pos.y)
		logging.info('avoid wall')
		posAndEnemyProb = sorted([(hexagon.distance(c, (0, 0)), c) for c in coordinates], reverse=True)
		return list(zip(*posAndEnemyProb))[1]


class spreadOwnBots(Escaping):

	def getPossibleMoves(self, bot):
		pass


class StatisticalEscaping(Escaping):

	def __init__(self, config):
		self.config = config

		self.jumpDirections = [
			( 0.5, AvoidWalls(config) ),
			( 0.3, ChaseEnemy(config) ),
			( 0.2, RunFromEnemy(config) ),
			#spreadOwnBots(config)
		]

		self.jumpStyles = [
			( 0.4, StraightDistance2Escaping(config) ),
			( 0.3, CurvedDistance2Escaping(config) ),
			( 0.2, Distance1Escaping(config) ),
			( 0.1, PretendToBeDead(config) ),
		]

		self.escapeMoves = []
		for dprob, direction in self.jumpDirections:
			for sprob, style in self.jumpStyles:
				probability = dprob * sprob
				escapeMove = (probability, direction, style)
				self.escapeMoves.append(escapeMove)

		self.movesWaitingForEvaluation = []
		defaultNotificationCenter.registerFunc(ID_START_ROUND_NOTIFICATION, self._analyzeOutcome)


	def _analyzeOutcome(self, notification):
		if not len(self.movesWaitingForEvaluation):
			return

		outcome = 1.10
		
		for event in notification.data['events']:
			#if event.event == 'die' and event.botId:
				#outcome -= 1.0

			# damage is sufficient, because I get it also when died 
			if event.event == 'damaged':
				outcome *= 0.5

		for index in self.movesWaitingForEvaluation:
			oldprob, direction, style = self.escapeMoves[index]
			newprob = oldprob * outcome
			self.escapeMoves[index] = (newprob, direction, style)

		self.movesWaitingForEvaluation = []

	def getPossibleMoves(self, bot):
		# choose tuple with probability
		# get sorted fields for direction and jump-styles
		# take best direction that applies to jump style
		# if there is none, take the best direction
		index = 0
		
		total = sum(p for p, d, s in self.escapeMoves)
		r = random.uniform(0, total)
		
		upto = 0
		for i, t in enumerate(self.escapeMoves):
			prob, direction, style = t
			if upto + prob >= r:
				index = i
				break
			upto += prob

		self.movesWaitingForEvaluation.append(index)
		prob, direction, style = self.escapeMoves[index]

		directionFields = direction.getPossibleMoves(bot)
		styleFields = style.getPossibleMoves(bot)
		
		for field in directionFields:
			if field in styleFields:
				return [field]

		return [directionFields[0]]

		