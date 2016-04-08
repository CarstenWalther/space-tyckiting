import unittest

from tyckiting_client.ai import base
from tyckiting_client.messages import Pos, Bot, Config


class BaseAiTest(unittest.TestCase):

    def setUp(self):
        self.ai = base.BaseAi(1, Config())

    def test_get_positions_in_origo_range(self):
        positions = set(self.ai.get_positions_in_range(x=0, y=0, radius=1))
        expected_positions = set((
            Pos(x=0, y=0),
            Pos(x=0, y=-1),
            Pos(x=1, y=-1),
            Pos(x=1, y=0),
            Pos(x=0, y=1),
            Pos(x=-1, y=1),
            Pos(x=-1, y=0),
        ))
        self.assertEqual(positions, expected_positions)

    def test_get_positions_in_zero_origo_range(self):
        positions = set(self.ai.get_positions_in_range(x=0, y=0, radius=0))
        expected_positions = set((
            Pos(x=0, y=0),
        ))
        self.assertEqual(positions, expected_positions)

    def test_get_positions_in_non_origo_range(self):
        positions = set(self.ai.get_positions_in_range(x=2, y=-3, radius=1))
        expected_positions = set((
            Pos(x=2, y=-3),
            Pos(x=2, y=-4),
            Pos(x=3, y=-4),
            Pos(x=3, y=-3),
            Pos(x=2, y=-2),
            Pos(x=1, y=-2),
            Pos(x=1, y=-3),
        ))
        self.assertEqual(positions, expected_positions)

    def test_get_valid_moves_center(self):
        bot = Bot(1, 'bot1', '1', pos={'x':0, 'y':0})
        positions = set(self.ai.get_valid_moves(bot))
        expected_positions = set((
            Pos(x=-2, y= 0),
            Pos(x=-2, y= 1),
            Pos(x=-2, y= 2),
            Pos(x=-1, y=-1),
            Pos(x=-1, y= 0),
            Pos(x=-1, y= 1),
            Pos(x=-1, y= 2),
            Pos(x= 0, y=-2),
            Pos(x= 0, y=-1),
            Pos(x= 0, y= 1),
            Pos(x= 0, y= 2),
            Pos(x= 1, y=-2),
            Pos(x= 1, y=-1),
            Pos(x= 1, y= 0),
            Pos(x= 1, y= 1),
            Pos(x= 2, y=-2),
            Pos(x= 2, y=-1),
            Pos(x= 2, y= 0),
        ))
        self.assertEqual(positions, expected_positions)
