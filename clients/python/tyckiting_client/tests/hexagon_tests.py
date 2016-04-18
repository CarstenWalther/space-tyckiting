import unittest

from tyckiting_client import hexagon

class HexagonTest(unittest.TestCase):

    def test_get_ring_center_radius_0(self):
        positions = set(hexagon.get_ring((0, 0), radius=0))
        expected_positions = set(
            [(0, 0)]
        )
        self.assertEqual(positions, expected_positions)

    def test_get_ring_center_radius_1(self):
        positions = set(hexagon.get_ring((0, 0), radius=1))
        expected_positions = set((
            (-1, 0),
            (-1, 1),
            ( 0,-1),
            ( 0, 1),
            ( 1,-1),
            ( 1, 0),
        ))
        self.assertEqual(positions, expected_positions)

    def test_get_ring_center_radius_2(self):
        positions = set(hexagon.get_ring((0, 0), radius=2))
        expected_positions = set((
            (-2, 0),
            (-2, 1),
            (-2, 2),
            (-1,-1),
            (-1, 2),
            ( 0,-2),
            ( 0, 2),
            ( 1,-2),
            ( 1, 1),
            ( 2,-2),
            ( 2,-1),
            ( 2, 0),
        ))
        self.assertEqual(positions, expected_positions)

    def test_get_ring_not_center_radius_1(self):
        positions = set(hexagon.get_ring((1, 2), radius=1))
        expected_positions = set((
            (0, 2),
            (0, 3),
            (1, 1),
            (1, 3),
            (2, 1),
            (2, 2),
        ))
        self.assertEqual(positions, expected_positions)

    def test_cube_add(self):
        self.assertEqual((2,-1), hexagon.cube_add((1,1), (1,-2)))

    def test_amoundOfHexagon(self):
        self.assertEqual(7, hexagon.totalAmountOfHexagons(1))
        self.assertEqual(19, hexagon.totalAmountOfHexagons(2))
        self.assertEqual(631, hexagon.totalAmountOfHexagons(14))

    def test_mirrorCoordinate_same_point(self):
        mirroredPoint = hexagon.mirrorCoordinate((1,1), (1,1))
        expectedMirroredPoint = (1,1)
        self.assertEqual(mirroredPoint, expectedMirroredPoint)

    def test_mirrorCoordinate_different_point(self):
        mirroredPoint = hexagon.mirrorCoordinate((0,1), (3,3))
        expectedMirroredPoint = (6,5)
        self.assertEqual(mirroredPoint, expectedMirroredPoint)

    def test_distance(self):
        pos1 = [-2, -7]
        pos2 = [2, 1]
        
        calculated_distance = hexagon.distance(pos1, pos2)
        expected_distance = 12
        self.assertEqual(calculated_distance, expected_distance)
        
        calculated_distance = hexagon.distance(pos2, pos1)
        self.assertEqual(calculated_distance, expected_distance)

    def test_distance_zero(self):
        pos1 = [2, 1]
        pos2 = [2, 1]
        
        calculated_distance = hexagon.distance(pos1, pos2)
        expected_distance = 0
        self.assertEqual(calculated_distance, expected_distance)
        
        calculated_distance = hexagon.distance(pos2, pos1)
        self.assertEqual(calculated_distance, expected_distance)

    def test_isInField_2_2_is_in_radius_2(self):
        result = hexagon.isInField((2,2), radius=2)
        expectedResult = False
        self.assertEqual(result, expectedResult)

    def test_extractValidCoordinates_center(self):
        coords = [(0,0), (1,0), (2,0), (3,0), (1,1), (2,2), (-2,2), (1,-2), (2,-4)]
        validCoords = hexagon.extractValidCoordinates(coords, radius=2)
        expectedValidCoords = set([(0,0), (1,0), (2,0), (1,1), (-2,2), (1,-2)])
        self.assertEqual(validCoords, expectedValidCoords)

    def test_extractValidCoordinates_with_offset(self):
        coords = [(2,1), (3,1), (4,1), (5,1), (2,0), (2,-1), (2,-2), (3,-1), (4,-3)]
        validCoords = hexagon.extractValidCoordinates(coords, radius=2, center=(2,1))
        expectedValidCoords = set([(2,1), (3,1), (4,1), (2,0), (2,-1), (3,-1)])
        self.assertEqual(validCoords, expectedValidCoords)

    def test_isStraightLine_dx(self):
        result = hexagon.isStraightLine((0,2), (2,2))
        expectedResult = True
        self.assertEqual(result, expectedResult)

    def test_isStraightLine_dy(self):
        result = hexagon.isStraightLine((2,2), (2,3))
        expectedResult = True
        self.assertEqual(result, expectedResult)

    def test_isStraightLine_dz(self):
        result = hexagon.isStraightLine((2,1), (4,-1))
        expectedResult = True
        self.assertEqual(result, expectedResult)

    def test_isStraightLine_not_straight(self):
        result = hexagon.isStraightLine((-1,0), (2,2))
        expectedResult = False
        self.assertEqual(result, expectedResult)