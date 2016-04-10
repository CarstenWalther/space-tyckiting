import random
import logging

from tyckiting_client import hexagon
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

class DontOvershootScanning(Scanning):

	def getPossibleScanPositions(self):
		return hexagon.getCircle(radius=self.config.field_radius-self.config.radar)
