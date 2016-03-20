import unittest

from tyckiting_client.ai import base
from tyckiting_client import messages

from mock import patch


class BaseAiTest(unittest.TestCase):

    def setUp(self):
        config = messages.Config(radius=14)
        self.ai = base.BaseAi(1, config)

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

    """
    def test_optimal_radar_around_origo(self):
        positions = set(self.ai.optimal_radar_around(x=0, y=0, radar=self.ai.config.radar))
        expected_positions = set((
            messages.Pos(x=2, y=-5),
            messages.Pos(x=5, y=-3),
            messages.Pos(x=3, y=2),
            messages.Pos(x=-2, y=5),
            messages.Pos(x=-5, y=3),
            messages.Pos(x=-3, y=-2),
        ))
        self.assertEqual(positions, expected_positions)

    def test_optimal_radar_around_not_origo(self):
        positions = set(self.ai.optimal_radar_around(x=3, y=2, radar=self.ai.config.radar))
        expected_positions = set((
            messages.Pos(x=5, y=-3),
            messages.Pos(x=8, y=-1),
            messages.Pos(x=6, y=4),
            messages.Pos(x=1, y=7),
            messages.Pos(x=-2, y=5),
            messages.Pos(x=0, y=0),
        ))
        self.assertEqual(positions, expected_positions)
    """

    def test_optimal_radars_on_field(self):
        positions = self.ai.optimal_radars_on_field(radar=self.ai.config.radar)
        expected_positions_subset = set((
            messages.Pos(x=0, y=0),
            messages.Pos(x=6, y=-14),
        ))
        self.assertTrue(positions.issuperset(expected_positions_subset))

    """
    def test_optimal_radars_on_small_field(self):
        config = messages.Config(fieldRadius=5)
        self.ai = base.BaseAi(1, config)
        positions = set(self.ai.optimal_radars_on_field(radar=self.ai.config.radar))
        expected_positions = set((
            messages.Pos(x=0, y=0),
            messages.Pos(x=2, y=-5),
            messages.Pos(x=5, y=-3),
            messages.Pos(x=3, y=2),
            messages.Pos(x=-2, y=5),
            messages.Pos(x=-5, y=3),
            messages.Pos(x=-3, y=-2),
        ))
        self.assertEqual(positions, expected_positions)
    """

    def test_increase_jradar_values(self):
        self.ai.increase_jradar_values()
        self.ai.jradar_values[messages.Pos(1,1)] = 25
        self.ai.jradar_values[messages.Pos(0,0)] = 10
        self.ai.increase_jradar_values()
        self.ai.increase_jradar_values()
        for key, value in self.ai.jradar_values.items():
            if key == messages.Pos(1,1):
                self.assertEqual(value, 27)
            elif key == messages.Pos(0,0):
                self.assertEqual(value, 12)
            else:
                self.assertEqual(value, 4)
        self.assertEqual(self.ai.get_biggest_jradar()[1], 27)
