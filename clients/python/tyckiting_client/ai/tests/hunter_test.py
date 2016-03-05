import unittest

from tyckiting_client.ai import hunter
from tyckiting_client import messages


class HunterAiTest(unittest.TestCase):

    def setUp(self):
        self.ai = hunter.Ai(1)

    """
    def test_get_edge_positions_in_range_1(self):
        positions = set(self.ai.get_edge_positions_in_range(x=0, y=0, radius=1))
        expected_positions = set((
            messages.Pos(x=0, y=-1),
            messages.Pos(x=1, y=-1),
            messages.Pos(x=1, y=0),
            messages.Pos(x=0, y=1),
            messages.Pos(x=-1, y=1),
            messages.Pos(x=-1, y=0),
        ))
        self.assertEqual(positions, expected_positions)

    def test_get_edge_positions_in_range_2(self):
        positions = set(self.ai.get_edge_positions_in_range(x=0, y=0, radius=2))
        expected_positions = set((
            messages.Pos(x=2, y=0),
            messages.Pos(x=2, y=-1),
            messages.Pos(x=2, y=-2),
            messages.Pos(x=1, y=-2),
            messages.Pos(x=0, y=-2),
            messages.Pos(x=-1, y=-1),
            messages.Pos(x=-2, y=0),
            messages.Pos(x=-2, y=1),
            messages.Pos(x=-2, y=2),
            messages.Pos(x=-1, y=2),
            messages.Pos(x=0, y=2),
            messages.Pos(x=1, y=1),
        ))
        self.assertEqual(positions, expected_positions)
    """
    
    def test_circle_1(self):
        positions = set(self.ai.circle(x=0, y=0, radius=1))
        expected_positions = set((
            messages.Pos(x=1, y=0),
            messages.Pos(x=0, y=1),
            messages.Pos(x=-1, y=1),
            messages.Pos(x=-1, y=0),
            messages.Pos(x=0, y=-1),
            messages.Pos(x=1, y=-1),
        ))
        self.assertEqual(positions, expected_positions)

    def test_circle_2(self):
        positions = set(self.ai.circle(x=0, y=0, radius=2))
        expected_positions = set((
            messages.Pos(x=2, y=0),
            messages.Pos(x=2, y=-1),
            messages.Pos(x=2, y=-2),
            messages.Pos(x=1, y=-2),
            messages.Pos(x=0, y=-2),
            messages.Pos(x=-1, y=-1),
            messages.Pos(x=-2, y=0),
            messages.Pos(x=-2, y=1),
            messages.Pos(x=-2, y=2),
            messages.Pos(x=-1, y=2),
            messages.Pos(x=0, y=2),
            messages.Pos(x=1, y=1),
        ))
        self.assertEqual(positions, expected_positions)

    def test_circle_3(self):
        positions = set(self.ai.circle(x=1, y=1, radius=3))
        expected_positions = set((
            messages.Pos(x=4, y=1),
            messages.Pos(x=3, y=2),
            messages.Pos(x=2, y=3),
            messages.Pos(x=1, y=4),
            messages.Pos(x=0, y=4),
            messages.Pos(x=-1, y=4),
            messages.Pos(x=-2, y=4),
            messages.Pos(x=-2, y=3),
            messages.Pos(x=-2, y=2),
            messages.Pos(x=-2, y=1),
            messages.Pos(x=-1, y=0),
            messages.Pos(x=0, y=-1),
            messages.Pos(x=1, y=-2),
            messages.Pos(x=2, y=-2),
            messages.Pos(x=3, y=-2),
            messages.Pos(x=4, y=-2),
            messages.Pos(x=4, y=-1),
            messages.Pos(x=4, y=0),
        ))
        self.assertEqual(positions, expected_positions)

    def test_pos_on_field(self):
        fr = 14
        self.assertTrue(self.ai.pos_on_field(x=0, y=0, field_radius=fr))
        self.assertTrue(self.ai.pos_on_field(x=1, y=1, field_radius=fr))
        self.assertTrue(self.ai.pos_on_field(x=-1, y=-1, field_radius=fr))
        self.assertTrue(self.ai.pos_on_field(x=7, y=7, field_radius=fr))
        self.assertTrue(self.ai.pos_on_field(x=14, y=0, field_radius=fr))
        self.assertTrue(self.ai.pos_on_field(x=0, y=14, field_radius=fr))
        self.assertTrue(self.ai.pos_on_field(x=-14, y=0, field_radius=fr))
        self.assertTrue(self.ai.pos_on_field(x=0, y=-14, field_radius=fr))
        self.assertFalse(self.ai.pos_on_field(x=15, y=-8, field_radius=fr))
        self.assertFalse(self.ai.pos_on_field(x=15, y=0, field_radius=fr))
        self.assertFalse(self.ai.pos_on_field(x=0, y=15, field_radius=fr))
        self.assertFalse(self.ai.pos_on_field(x=-15, y=0, field_radius=fr))
        self.assertFalse(self.ai.pos_on_field(x=0, y=-15, field_radius=fr))
        self.assertFalse(self.ai.pos_on_field(x=4, y=11, field_radius=fr))

    def test_circle_on_field(self):
        config = messages.Config(fieldRadius=14)
        self.ai.config = config
        positions = set(self.ai.circle_on_field(x=13, y=0, radius=2, field_radius=14))
        expected_positions = set((
            messages.Pos(x=14, y=-2),
            messages.Pos(x=13, y=-2),
            messages.Pos(x=12, y=-1),
            messages.Pos(x=11, y=0),
            messages.Pos(x=11, y=1),
            messages.Pos(x=11, y=2),
            messages.Pos(x=12, y=2),
        ))
        self.assertEqual(positions, expected_positions)


