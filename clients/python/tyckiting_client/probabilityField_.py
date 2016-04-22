
from tyckiting_client import hexagon
from tyckiting_client.utilities import *
import logging

import scipy.misc

import numpy as np

class ProbabilityField(object):

	def __init__(self, radius, totalProbability=1):
		self.dimension = radius * 2 + 1
		self.totalProbability = totalProbability
		self.field = np.ones((self.dimension, self.dimension))
		self.field /= (self.field.sum() / totalProbability)

		#self.field = dict()
		#self.totalProbability = totalProbability
		#self.fieldRadius = radius
		#self._initializeField(radius, totalProbability)

	#def _initializeField(self, radius, totalProbability):
		#fieldAmount = hexagon.totalAmountOfHexagons(radius)
		#for pos in hexagon.getCircle(radius):
			#self.field[pos] = totalProbability / fieldAmount

	def getBestCoordinates(self, radius, amount=1):
		result = []

		tmpField = np.ones_like(self.field) * self.field

		while len(result) < amount:
			blurredTmpField = self._combsum(tmpField, radius)
			pos = np.unravel_index(blurredTmpField.argmax(), blurredTmpField.shape)
			result.append(self._translateFromField(pos))

			# reset this spot
			coords = self._filterValid( self._translateIntoField( self._getCircle(radius, pos[0], pos[1]) ) )
			tmpField[ coords[:,0], coords[:,1] ] = 0.0
			
		return result

		"""
		allCoordinates = set(hexagon.getCircle(self.fieldRadius))
		usedCoordinates = set()

		while len(result) < amount:
			bestPosition = None
			bestPositionScore = -1

			for coord in allCoordinates:
				positions = hexagon.getCircle(radius, coord[0], coord[1])
				positions = hexagon.extractValidCoordinates(positions, self.fieldRadius)
				positions = positions - usedCoordinates
				
				totalProbability = sum(self.field[position] for position in positions)
				if totalProbability > bestPositionScore:
					bestPosition = coord
					bestPositionScore = totalProbability
			
			result.append(bestPosition)
			usedCoordinates |= set(hexagon.getCircle(radius, bestPosition[0], bestPosition[1]))
		"""

	"""
	Own cached and vectorized functions for hexagon field 
	"""
	@memorize
	def _getKernel(self, radius=1):
		return np.matrix(list(hexagon.getCircle(radius)))

	def _getCircle(self, radius=1, x=0, y=0):
		coord = np.array([x, y])
		return self._getKernel(radius) + coord

	def _rebalance(self):
		self.field /= (self.field.sum() / self.totalProbability)

	def _translateIntoField(self, coords):
		halfDim = np.trunc( np.array(self.field.shape) / 2 )
		halfDim = halfDim.astype(int)
		return coords + halfDim

	def _translateFromField(self, coords):
		halfDim = np.trunc( np.array(self.field.shape) / 2 )
		halfDim = halfDim.astype(int)
		return coords - halfDim

	def _filterValid(self, coords):
		x_in_range = np.logical_and(0 <= coords[:,0], coords[:,0] < self.field.shape[0])
		y_in_range = np.logical_and(0 <= coords[:,1], coords[:,1] < self.field.shape[1])
		npAFilter = np.logical_and(x_in_range, y_in_range)
		npAFilter = np.squeeze(np.asarray(npAFilter))
		return coords[np.ix_(npAFilter)]

	def clear(self, radius=None, x=0, y=0):
		if not radius:
			radius = self.fieldRadius

		coords = self._getCircle(radius, x, y)
		coords = self._translateIntoField( coords )
		coords = self._filterValid( coords )
		self.field[ coords[:,0], coords[:,1] ] = 0.0

		self._rebalance()

		#positions = hexagon.getCircle(radius, x, y)
		#for position in positions:
			#if position in self.field:
				#self.field[position] = 0.0

	def set(self, pos, value):
		pos = self._translateIntoField(np.array(pos))
		print('set ', pos, value)
		self.field[pos] = value

	def setEnemy(self, pos, value):
		pos = self._translateIntoField(np.array(pos))
		self.field[pos] = value
		self._rebalance()

	def get(self, pos):
		pos = self._translateIntoField(np.array(pos))
		return self.field[pos]

	def _blur(self, field, radius):
		newField = np.zeros(field.shape)
		scipy.misc.imsave('newField.png', newField)

		for x in range(newField.shape[0]):
			for y in range(newField.shape[1]):
				coords = self._filterValid( self._getCircle(radius, x, y) )
				newField[x,y] = np.average(field[coords[:,0], coords[:,1]])
		scipy.misc.imsave('newField_blur.png', newField)

		return newField

	def _combsum(self, field, radius):
		newField = np.zeros(field.shape)
		scipy.misc.imsave('newField.png', newField)

		for x in range(newField.shape[0]):
			for y in range(newField.shape[1]):
				coords = self._filterValid( self._getCircle(radius, x, y) )
				newField[x,y] = np.sum(field[coords[:,0], coords[:,1]])
		scipy.misc.imsave('newField_blur.png', newField)

		return newField

	def blur(self, radius):
		self.field = self._blur(self.field, radius)

		#newField = dict()
		#for pos in hexagon.getCircle(self.fieldRadius):
			#newField[pos] = self._getBlurSum(pos, radius)
		#self.field = newField

	#def _getBlurSum(self, pos, radius):
		#possibleMoveOriginFields = hexagon.getCircle(radius, pos[0], pos[1])
		#possibleMoveOriginFields = hexagon.extractValidCoordinates(possibleMoveOriginFields, self.fieldRadius)
		#possibilitySum = sum(self.field[position] for position in possibleMoveOriginFields)
		#return possibilitySum / len(possibleMoveOriginFields)
