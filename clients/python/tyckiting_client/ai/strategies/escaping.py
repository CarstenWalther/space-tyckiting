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
			# dont need: inverse to distance to mid if normalized
			#distToWall = self.distanceToWall(coordinate) 
			#distToWall /= self.config.field_radius

			distToMid = hexagon.distance(coordinate, (0,0))
			# normalize
			distToMid /= self.config.field_radius
			# fit to u shape curve to set mid and wall to 1 and inner circle to 0
			distToInnerCircle = 16 * (distToMid - 0.5)**4

			gameField = GameField(self.config)
			enemyProbability = gameField.enemyProbability(coordinate)

			distToClosestTeamMate = min([hexagon.distance( (b.pos.x,b.pos.y), (bot.pos.x, bot.pos.y) ) for b in self.bots if b.bot_id != bot.bot_id])
			distToClosestTeamMate /= self.config.field_radius

			table[i,:] = np.array([distToInnerCircle, enemyProbability, distToClosestTeamMate])

		# normalize enemyProb
		table[:,1] = table[:,1] / table[:,1].sum()
		
		#for i in range(3):
			#values = table[:,i]
			##table[:,i] = (values - values.min()) / (values.max() - values.min())
			#table[:,i] = values / values.sum()

		# minimize dist to inner circle
		# maximize enemyProbability
		# maximize dist to own bots
		scores = table[:,0] + 1-table[:,1] + 1-table[:,2]
		return [coordinates[scores.argmin()]]


# list of tuples (probability, ....)
# return (index, element)
def chooseByProbability(plist):
	index = 0
	total = sum(p for p, *_ in plist)	
	r = random.uniform(0, total)
	for i, t in enumerate(plist):
		r -= t[0]
		if r < 0:
			index = i
			break
	return (index, plist[index])


class StatisticalEscaping(Escaping):

	def __init__(self, config):
		self.config = config

		self.jumpDirections = [
			( 0.5, AvoidWalls(config), 'AvoidWalls' ),
			( 0.3, ChaseEnemy(config), 'ChaseEnemy' ),
			( 0.2, RunFromEnemy(config), 'RunFromEnemy' ),
			#spreadOwnBots(config)
		]

		self.jumpStyles = [
			( 0.4, StraightDistance2Escaping(config), 'StraightDistance2Escaping' ),
			( 0.3, CurvedDistance2Escaping(config), 'CurvedDistance2Escaping' ),
			( 0.2, Distance1Escaping(config), 'Distance1Escaping' ),
			#( 0.1, PretendToBeDead(config), 'PretendToBeDead' ),
		]

		self.escapeMoves = []
		for dprob, direction, desc_dir in self.jumpDirections:
			for sprob, style, desc_style in self.jumpStyles:
				probability = dprob * sprob
				escapeMove = (probability, direction, style, '{:s} {:s}'.format(desc_dir, desc_style))
				self.escapeMoves.append(escapeMove)

		self.movesWaitingForEvaluation = []
		defaultNotificationCenter.registerFunc(ID_START_ROUND_NOTIFICATION, self._analyzeOutcome)

	def logCurrentProbabilities(self):
		logging.info('# Escape Strategies:')
		sortedList = sorted([(e[0], e[3]) for e in self.escapeMoves], reverse=True)
		for p,desc in sortedList:
			logging.info('  {:0.5f} {:s}'.format(p, desc))

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
			oldprob, direction, style, desc = self.escapeMoves[index]
			newprob = oldprob * outcome
			self.escapeMoves[index] = (newprob, direction, style, desc)

		self.movesWaitingForEvaluation = []

		self.logCurrentProbabilities()

	def getPossibleMoves(self, bot):
		# choose tuple with probability
		# get sorted fields for direction and jump-styles
		# take best direction that applies to jump style
		# if there is none, take the best direction
		index, move = chooseByProbability(self.escapeMoves)

		self.movesWaitingForEvaluation.append(index)
		prob, direction, style, desc = move

		directionFields = direction.getPossibleMoves(bot)
		styleFields = style.getPossibleMoves(bot)
		
		for field in directionFields:
			if field in styleFields:
				return [field]

		return [directionFields[0]]


# similar to StatisticalEscaping, but evaluates strategies individually
class StatisticalEscaping2(Escaping):

	def __init__(self, config):
		self.config = config

		self.jumpDirections = [
			( 0.5, AvoidWalls(config), 'AvoidWalls' ),
			( 0.3, ChaseEnemy(config), 'ChaseEnemy' ),
			( 0.2, RunFromEnemy(config), 'RunFromEnemy' ),
			#spreadOwnBots(config)
		]

		self.jumpStyles = [
			( 0.4, StraightDistance2Escaping(config), 'StraightDistance2Escaping' ),
			( 0.3, CurvedDistance2Escaping(config), 'CurvedDistance2Escaping' ),
			( 0.2, Distance1Escaping(config), 'Distance1Escaping' ),
			#( 0.1, PretendToBeDead(config), 'PretendToBeDead' ),
		]

		# [(     0          ,      0)      , (1,0)]
		# [(index(direction), index(style)), ...
		self.movesWaitingForEvaluation = []
		defaultNotificationCenter.registerFunc(ID_START_ROUND_NOTIFICATION, self._analyzeOutcome)

	def logCurrentProbabilities(self):
		logging.info('# Escape Strategies:')
		sortedList = sorted([(e[0], e[2]) for e in (self.jumpDirections + self.jumpStyles)], reverse=True)
		for p,desc in sortedList:
			logging.info('  {:0.5f} {:s}'.format(p, desc))

	def _analyzeOutcome(self, notification):
		if not len(self.movesWaitingForEvaluation):
			return

		outcome = 1.25
		
		for event in notification.data['events']:
			# damage is sufficient, because I get it also when died 
			if event.event == 'damaged':
				outcome *= 0.5

		for index_dir, index_style in self.movesWaitingForEvaluation:
			self.jumpDirections[index_dir][0] *= outcome
			self.jumpStyles[index_style][0] *= outcome

		self.movesWaitingForEvaluation = []

		self.logCurrentProbabilities()

	def getPossibleMoves(self, bot):
		logging.info('choose moves:')
		index_dir, direction_tuple = chooseByProbability(self.jumpDirections)
		index_style, style_tuple = chooseByProbability(self.jumpStyles)

		self.movesWaitingForEvaluation.append((index_dir, index_style))

		prob_dir, direction, *_ = direction_tuple
		prob_style, style, *_ = style_tuple

		directionFields = direction.getPossibleMoves(bot)
		styleFields = style.getPossibleMoves(bot)
		
		for field in directionFields:
			if field in styleFields:
				return [field]

		return [directionFields[0]]

		