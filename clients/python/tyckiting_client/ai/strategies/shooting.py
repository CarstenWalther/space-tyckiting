import random
import logging

from tyckiting_client import hexagon
from tyckiting_client.messages import Pos

class Shooting(object):

	def __init__(self, config):
		self.config = config

	def getShootPositions(self, targetPos, shooterAmount):
		coordLists = self.getPossibleShootPositions(targetPos, shooterAmount)
		return random.choice(coordLists)

	def getPossibleShootPositions(self, targetPos, shooterAmount):
		raise NotImplementedError()

class RandomShooting(Shooting):

	def getPossibleShootPositions(self, targetPos, shooterAmount):
		coords = []
		for i in range(shooterAmount):
			coords.append(hexagon.getCircle(self.config.move, targetPos.x, targetPos.y))

class SpreadShooting(Shooting):

	'''
	maximizes hit chance but not damage
	'''

	def __init__(self, config):
		super(SpreadShooting, self).__init__(config)
		self.shotOffsets = [[(-1,0), (1,-1), (0,1)], [(0,-1), (1,0), (-1,1)]]

	def getPossibleShootPositions(self, targetPos, shooterAmount):
		if shooterAmount == 1:
			return self.getPositionsOneShot(targetPos)
		if shooterAmount == 2:
			return self.getPositionsTwoShots(targetPos)
		if shooterAmount == 3:
			return self.getPositionsThreeShots(targetPos)

	def getPositionsOneShot(self, targetPos):
		return [[x] for x in hexagon.get_ring(targetPos, radius=1)]

	def getPositionsTwoShots(self, targetPos):
		return [[x, hexagon.mirrorCoordinate(x, targetPos)] for x in hexagon.get_ring(targetPos, radius=1)]

	def getPositionsThreeShots(self, targetPos):
		return [[hexagon.cube_add(targetPos, offset) for offset in offsets] for offsets in self.shotOffsets]
		




