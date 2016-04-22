import unittest

from tyckiting_client.ai.strategies import tracking
from tyckiting_client import hexagon


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
		self.assertEqual(field.get((0,0)), tracking.BALANCED_PATTERN['stay'])
		self.assertEqual(field.get((1,0)), tracking.BALANCED_PATTERN['dist1'])
		self.assertEqual(field.get((2,0)), tracking.BALANCED_PATTERN['dist2Straight'])
		self.assertEqual(field.get((1,1)), tracking.BALANCED_PATTERN['dist2Curve'])

	def test_getShootCoordinates_enemy_stays(self):
		tracker = tracking.Tracker(tracking.STAY_PATTERN)
		tracker.trackedTarget = (1,1)
		coordinates = tracker.getShootCoordinates(1)
		expectedShootCoordinate = (1,1)
		self.assertEqual(len(coordinates), 1)
		self.assertEqual(coordinates[0], expectedShootCoordinate)

	def test_getShootCoordinates_two_shots_enemy_stays(self):
		tracker = tracking.Tracker(tracking.STAY_PATTERN)
		tracker.trackedTarget = (1,1)
		coordinates = tracker.getShootCoordinates(2)
		expectedShootCoordinate = (1,1)
		self.assertEqual(len(coordinates), 2)
		self.assertEqual(coordinates[0], expectedShootCoordinate)
		self.assertEqual(coordinates[1], expectedShootCoordinate)

	def test_getShootCoordinates_avoid_selfhit(self):
		tracker = tracking.Tracker(tracking.STRAIGHT_DISTANCE2_PATTERN)
		tracker.trackedTarget = (0,0)
		teamPositions = [(2,-2), (-1,-1), (0,2), (-2,1)]
		coordinates = tracker.getShootCoordinates(1, teamPositions)
		expectedShootCoordinate = (2,0)
		self.assertEqual(coordinates[0], expectedShootCoordinate)

	def test_getShootCoordinates_avoid_selfhit_offset(self):
		tracker = tracking.Tracker(tracking.STRAIGHT_DISTANCE2_PATTERN)
		tracker.trackedTarget = (4,4)
		teamPositions = [(6,2), (3,3), (4,6), (2,5)]
		coordinates = tracker.getShootCoordinates(1, teamPositions)
		expectedShootCoordinate = (6,4)
		self.assertEqual(coordinates[0], expectedShootCoordinate)

	def test_getShootCoordinates_avoid_selfhit_distance_3(self):
		tracker = tracking.Tracker(tracking.STRAIGHT_DISTANCE2_PATTERN)
		tracker.trackedTarget = (0,0)
		teamPositions = [(3,-2), (3,-3), (2,-3), (1,-3), (0,-3), (-1,-2), (-2,-1), (-3,0), 
						(-3,1), (-3,2), (-3,3), (-2,3), (1,3), (0,3), (1,2)]
		coordinates = tracker.getShootCoordinates(1, teamPositions)
		expectedShootCoordinate = (2,0)
		self.assertEqual(coordinates[0], expectedShootCoordinate)

	def test_getShootCoordinates_at_edge(self):
		custom_pattern = {'stay':0, 'dist1':1, 'dist2Straight':0, 'dist2Curve':0}
		tracker = tracking.Tracker(custom_pattern)
		tracker.trackedTarget = (14,0)
		coordinates = tracker.getShootCoordinates(1)
		expectedShootCoordinate = (13,0)
		self.assertEqual(coordinates[0], expectedShootCoordinate)
