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
        self.ai.reset_jradar_field()
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

    def test_reset_jradar(self):
        self.ai.reset_jradar_field()
        self.ai.increase_jradar_values()
        self.ai.increase_jradar_values()
        self.ai.jradar_values[messages.Pos(1,0)] = 25
        self.ai.jradar_values[messages.Pos(0,0)] = 10
        self.ai.reset_jradar(0,0)
        self.assertEqual(self.ai.get_biggest_jradar()[1], 3)
        self.assertEqual(self.ai.jradar_values[messages.Pos(1,0)], self.ai.jradar_initial_value)
        self.assertEqual(self.ai.jradar_values[messages.Pos(0,0)], self.ai.jradar_initial_value)
        self.assertEqual(self.ai.jradar_values[messages.Pos(-4,0)], 3)
        self.assertEqual(self.ai.jradar_values[messages.Pos(0,14)], 3)

    def test_reset_jradar_field(self):
        self.ai.reset_jradar_field()
        self.ai.jradar_values[messages.Pos(1,0)] = 25
        self.ai.jradar_values[messages.Pos(0,0)] = 25
        self.ai.jradar_values[messages.Pos(0,1)] = 25
        self.ai.reset_jradar_field()
        self.assertEqual(self.ai.jradar_values[messages.Pos(1,0)], self.ai.jradar_initial_value)
        self.assertEqual(self.ai.jradar_values[messages.Pos(0,0)], self.ai.jradar_initial_value)
        self.assertEqual(self.ai.jradar_values[messages.Pos(0,1)], self.ai.jradar_initial_value)
        self.assertEqual(self.ai.jradar_values[messages.Pos(1,1)], self.ai.jradar_initial_value)

    def test_calc_jradar_combination_value(self):
        self.ai.reset_jradar_field()
        self.assertEqual(self.ai.calc_jradar_combination_value(0, 0), 37*self.ai.jradar_initial_value)

    def test_get_biggest_jradar_points(self):
        self.ai.reset_jradar_field()
        self.ai.jradar_values[messages.Pos(0,0)] = 11
        self.ai.jradar_values[messages.Pos(3,0)] = 11
        self.ai.jradar_values[messages.Pos(-3,0)] = 11
        points = set(self.ai.get_biggest_jradar_points())
        expected_points = set([
            (messages.Pos(x=0, y=0), 67)
        ])
        self.assertEqual(points, expected_points)

    def test_get_biggest_jradar_points_2(self):
        self.ai.reset_jradar_field()
        self.ai.jradar_values[messages.Pos(0,0)] = 11
        self.ai.jradar_values[messages.Pos(2,0)] = 11
        self.ai.jradar_values[messages.Pos(-3,0)] = 11
        points = set(self.ai.get_biggest_jradar_points())
        expected_points = set([
            (messages.Pos(x=0, y=0), 67),
            (messages.Pos(x=-1, y=0), 67),
            (messages.Pos(x=0, y=-1), 67),
            (messages.Pos(x=-1, y=1), 67)
        ])
        self.assertEqual(points, expected_points)

    def test_get_single_biggest_jradar_points(self):
        self.ai.reset_jradar_field()
        self.ai.jradar_values[messages.Pos(0,0)] = 11
        self.ai.jradar_values[messages.Pos(3,0)] = 11
        self.ai.jradar_values[messages.Pos(-3,0)] = 11
        point = self.ai.get_single_biggest_jradar_points()
        self.assertEqual(point, (messages.Pos(0,0), 67))

    def test_get_positions_in_range_1(self):
        positions = set(self.ai.get_positions_in_range(0, 0, 3))
        expected_positions = set([
            messages.Pos(x=0, y=0)
        ])
        self.assertTrue(expected_positions.issubset(positions))

    def test_get_positions_in_range_2(self):
        positions = set(self.ai.get_positions_in_range(1, 1, 3))
        expected_positions = set([
            messages.Pos(x=1, y=1)
        ])
        self.assertEqual(len(positions), 37)
        self.assertTrue(expected_positions.issubset(positions))

    def test_get_positions_in_range_3(self):
        positions = set(self.ai.get_positions_in_range(0, 0, 1))
        expected_positions = set([
            messages.Pos(x=0, y=0),
            messages.Pos(x=1, y=0),
            messages.Pos(x=0, y=1),
            messages.Pos(x=-1, y=1),
            messages.Pos(x=-1, y=0),
            messages.Pos(x=0, y=-1),
            messages.Pos(x=1, y=-1)
        ])
        self.assertEqual(positions, expected_positions)

    def test_get_positions_in_range_wo_cur_pos_1(self):
        positions = set(self.ai.get_positions_in_range_wo_cur_pos(0, 0, 3))
        expected_positions = set([
            messages.Pos(x=0, y=0)
        ])
        self.assertFalse(expected_positions.issubset(positions))

    def test_get_positions_in_range_wo_cur_pos_2(self):
        positions = set(self.ai.get_positions_in_range_wo_cur_pos(1, 1, 3))
        expected_positions = set([
            messages.Pos(x=1, y=1)
        ])
        self.assertFalse(expected_positions.issubset(positions))

    def test_should_i_move(self):
        bot = messages.Bot(0, "potti", 0)

        bot.detected = False
        bot.panic_counter = 0
        (ebot, mybool) = self.ai.should_i_move(bot, 2)

        bot.detected = True
        (ebot, mybool) = self.ai.should_i_move(bot, 2)
        self.assertTrue(mybool)
        ebot.detected = False
        (ebot, mybool) = self.ai.should_i_move(ebot, 2)
        self.assertTrue(mybool)
        (ebot, mybool) = self.ai.should_i_move(ebot, 2)
        self.assertFalse(mybool)

