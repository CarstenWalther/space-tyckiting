import logging

from tyckiting_client.ai.strategies import escaping
from tyckiting_client.utilities import chooseByProbability
from tyckiting_client.notifications import defaultNotificationCenter
from tyckiting_client.notifications import ID_START_ROUND_NOTIFICATION

class StatisticalEscaping(escaping.Escaping):

	def __init__(self, config):
		self.config = config

		self.jumpDirections = [
			( 0.5, escaping.AvoidWalls(config), 'AvoidWalls' ),
			( 0.3, escaping.ChaseEnemy(config), 'ChaseEnemy' ),
			( 0.2, escaping.RunFromEnemy(config), 'RunFromEnemy' ),
		]

		self.jumpStyles = [
			( 0.4, escaping.StraightDistance2Escaping(config), 'StraightDistance2Escaping' ),
			( 0.3, escaping.CurvedDistance2Escaping(config), 'CurvedDistance2Escaping' ),
			( 0.2, escaping.Distance1Escaping(config), 'Distance1Escaping' ),
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
class StatisticalEscaping2(escaping.Escaping):

	def __init__(self, config):
		self.config = config

		self.jumpDirections = [
			( 0.5, escaping.AvoidWalls(config), 'AvoidWalls' ),
			( 0.3, escaping.ChaseEnemy(config), 'ChaseEnemy' ),
			( 0.2, escaping.RunFromEnemy(config), 'RunFromEnemy' ),
		]

		self.jumpStyles = [
			( 0.4, escaping.StraightDistance2Escaping(config), 'StraightDistance2Escaping' ),
			( 0.3, escaping.CurvedDistance2Escaping(config), 'CurvedDistance2Escaping' ),
			( 0.2, escaping.Distance1Escaping(config), 'Distance1Escaping' ),
		]

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
			if event.event == 'damaged':
				outcome *= 0.5

		for index_dir, index_style in self.movesWaitingForEvaluation:
			oldprob, strategy, description = self.jumpDirections[index_dir]
			newprob = oldprob * outcome
			self.jumpDirections[index_dir] = (newprob, strategy, description)

			oldprob, strategy, description = self.jumpStyles[index_style]
			newprob = oldprob * outcome
			self.jumpStyles[index_style] = (newprob, strategy, description)

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