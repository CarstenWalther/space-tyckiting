from tyckiting_client.notifications import defaultNotificationCenter
from tyckiting_client.notifications import ID_END_ROUND_NOTIFICATION
from tyckiting_client.notifications import ID_START_ROUND_NOTIFICATION
from tyckiting_client.probabilityField import ProbabilityField

from tyckiting_client.utilities import *

class GameField:
	class DefaultGameField:
		def __init__(self, config):
			logging.info('##### GameField created #####')
			self.config = config
			self.enemyProbabilityField = ProbabilityField(config.field_radius, self.config.bots)
			defaultNotificationCenter.registerFunc(ID_END_ROUND_NOTIFICATION, self._mindOwnScans)
			defaultNotificationCenter.registerFunc(ID_START_ROUND_NOTIFICATION, self._mindEventAndBots)

		def __str__(self):
			return repr(self) + self.config

		def _mindOwnScans(self, notification):
			for action in notification.data['actions']:
				if action.type == 'radar':
					self.enemyProbabilityField.clear(self.config.radar, action.x, action.y)

		@log_execution_time
		def _mindEventAndBots(self, notification):
			for bot in notification.data['bots']:
				self.enemyProbabilityField.clear(self.config.see, bot.pos.x, bot.pos.y)
			for event in notification.data['events']:
				if event.event == 'see' or event.event == 'radarEcho':
					pos = (event.pos.x, event.pos.y)
					self.enemyProbabilityField.set(pos, 1.0)
				elif event.event == 'die':
					# think about cleaning the possibilities in the area
					pass
			self.enemyProbabilityField.blur(self.config.move)

	instance = None
	def __init__(self, config):
		if not GameField.instance:
			GameField.instance = GameField.DefaultGameField(config)

	def __getattr__(self, name):
		return getattr(self.instance, name)

	def enemyProbability(self, pos):
		return self.instance.enemyProbabilityField.get(pos)
