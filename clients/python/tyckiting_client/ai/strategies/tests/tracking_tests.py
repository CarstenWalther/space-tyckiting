import unittest

from tyckiting_client.ai.strategies import tracking

class TrackingTest(unittest.TestCase):

	def test_updateCounter_dist2Straight(self):
		tracker = tracking.Tracker(tracking.STRAIGHT_DISTANCE2_PATTERN)
		tracker.knownEnemyPositions.append((1,1))
		tracker._updateCounter([(3,1)])
		expectedDictionary = {'stay':0, 'dist1':0, 'dist2Straight':3, 'dist2Curve':0}
		self.assertEqual(tracker.movementCounter, expectedDictionary)

	def test_updateCounter_stay(self):
		tracker = tracking.Tracker(tracking.STRAIGHT_DISTANCE2_PATTERN)
		tracker.knownEnemyPositions.append((1,1))
		tracker._updateCounter([(1,1)])
		expectedDictionary = {'stay':1, 'dist1':0, 'dist2Straight':2, 'dist2Curve':0}
		self.assertEqual(tracker.movementCounter, expectedDictionary)

	def test_updateCounter_prefer_more_probable_move(self):
		tracker = tracking.Tracker(tracking.STRAIGHT_DISTANCE2_PATTERN)
		tracker.knownEnemyPositions.append((1,1))
		tracker._updateCounter([(1,1),(2,1),(3,1)])
		expectedDictionary = {'stay':0, 'dist1':0, 'dist2Straight':3, 'dist2Curve':0}
		self.assertEqual(tracker.movementCounter, expectedDictionary)

	def test_updateCounter_multiple_sources_prefer_most_probable(self):
		tracker = tracking.Tracker(tracking.STRAIGHT_DISTANCE2_PATTERN)
		tracker.knownEnemyPositions.append((1,1))
		tracker.knownEnemyPositions.append((2,0))
		tracker._updateCounter([(2,2)])
		expectedDictionary = {'stay':0, 'dist1':0, 'dist2Straight':3, 'dist2Curve':0}
		self.assertEqual(tracker.movementCounter, expectedDictionary)

	def test_createField(self):
		tracker = tracking.Tracker(tracking.BALANCED_PATTERN)
		target = (0,0)
		field = tracker._createField(target)
		self.assertEqual(field.field[(0,0)], tracking.BALANCED_PATTERN['stay'])
		self.assertEqual(field.field[(1,0)], tracking.BALANCED_PATTERN['dist1'])
		self.assertEqual(field.field[(2,0)], tracking.BALANCED_PATTERN['dist2Straight'])
		self.assertEqual(field.field[(1,1)], tracking.BALANCED_PATTERN['dist2Curve'])

	def test_getShootCoordinates_enemy_stays(self):
		tracker = tracking.Tracker(tracking.STAY_PATTERN)
		tracker.trackedTarget = (1,1)
		coordinates = tracker.getShootCoordinates(1)
		expectedShootCoordinate = (1,1)
		self.assertEqual(len(coordinates), 1)
		self.assertEqual(coordinates[0], expectedShootCoordinate)