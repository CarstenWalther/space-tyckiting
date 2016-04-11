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