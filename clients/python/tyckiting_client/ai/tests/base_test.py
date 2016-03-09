import unittest

from tyckiting_client.ai import base
from tyckiting_client import messages

from mock import patch


class BaseAiTest(unittest.TestCase):

    def setUp(self):
        self.ai = base.BaseAi(1)

    def test_get_positions_in_origo_range(self):
        positions = set(self.ai.get_positions_in_range(x=0, y=0, radius=1))
        expected_positions = set((
            messages.Pos(x=0, y=0),
            messages.Pos(x=0, y=-1),
            messages.Pos(x=1, y=-1),
            messages.Pos(x=1, y=0),
            messages.Pos(x=0, y=1),
            messages.Pos(x=-1, y=1),
            messages.Pos(x=-1, y=0),
        ))
        self.assertEqual(positions, expected_positions)

    def test_get_positions_in_zero_origo_range(self):
        positions = set(self.ai.get_positions_in_range(x=0, y=0, radius=0))
        expected_positions = set((
            messages.Pos(x=0, y=0),
        ))
        self.assertEqual(positions, expected_positions)

    def test_get_positions_in_non_origo_range(self):
        positions = set(self.ai.get_positions_in_range(x=2, y=-3, radius=1))
        expected_positions = set((
            messages.Pos(x=2, y=-3),
            messages.Pos(x=2, y=-4),
            messages.Pos(x=3, y=-4),
            messages.Pos(x=3, y=-3),
            messages.Pos(x=2, y=-2),
            messages.Pos(x=1, y=-2),
            messages.Pos(x=1, y=-3),
        ))
        self.assertEqual(positions, expected_positions)

    @patch('random.randint', return_value=1)
    def test_triangle_points_1(self, mocked_randint):
        positions = set(self.ai.triangle_points(x=0, y=0, radius=1))
        expected_positions = set((
            messages.Pos(x=1, y=-1),
            messages.Pos(x=0, y=1),
            messages.Pos(x=-1, y=0),
        ))
        self.assertEqual(positions, expected_positions)

    @patch('random.randint', return_value=2)
    def test_triangle_points_2(self, mocked_randint):
        positions = set(self.ai.triangle_points(x=0, y=0, radius=1))
        expected_positions = set((
            messages.Pos(x=1, y=0),
            messages.Pos(x=-1, y=1),
            messages.Pos(x=0, y=-1),
        ))
        self.assertEqual(positions, expected_positions)
