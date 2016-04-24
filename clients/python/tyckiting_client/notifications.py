# Notification.data is expected to be {actions={}}
ID_END_ROUND_NOTIFICATION = 'end of round'

# Notification.data is expected to be {bots={}, events={}}
ID_START_ROUND_NOTIFICATION = 'start of round'


class Notification(object):
	def __init__(self, identifier, data):
		self.identifier = identifier
		self.data = data


class NotificationCenter(object):
	def __init__(self):
		self.listeningFunctions = dict()

	def registerFunc(self, identifier, func):
		if not identifier in self.listeningFunctions:
			self.listeningFunctions[identifier] = list()

		self.listeningFunctions[identifier].append(func)

	def send(self, notification):
		if not notification.identifier in self.listeningFunctions:
			return
		
		for listener in self.listeningFunctions[notification.identifier]:
			listener(notification)


defaultNotificationCenter = NotificationCenter()