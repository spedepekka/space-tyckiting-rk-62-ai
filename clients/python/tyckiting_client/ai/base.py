import random

from tyckiting_client import messages
from tyckiting_client import actions


class BaseAi:

    def __init__(self, team_id, config=None):
        """
        Initializes the AI, storing the configuration values as fields

        Args:
            team_id: Team identifier as an integer, shouldn't be needed
            config: Dictionary of game parameters
        """
        self.team_id = team_id
        self.config = config or {}
        self.field_points = None

    def move(self, bots, events):
        """
        Perform bot actions, based on events from last round.

        This is the only method that needs to be implemented in custom AIs.

        Args:
            bots: List of bot states for own team
            events: List of events form previous round

        Returns:
            List of actions to perform this round.
        """

        raise NotImplementedError()

    def get_valid_moves(self, bot):
        return self.get_positions_in_range(x=bot.pos.x, y=bot.pos.y, radius=self.config.move)

    def get_valid_moves_wo_cur_pos(self, bot):
        return self.get_positions_in_range(x=bot.pos.x, y=bot.pos.y, radius=self.config.move)

    # All moves with max distance (fails when close the field border)
    def get_valid_edge_moves(self, bot):
        return self.get_edge_positions_in_range(x=bot.pos.x, y=bot.pos.y, radius=self.config.move)

    # All moves with max distance (field border fixed)
    def get_valid_edge_moves_in_field(self, bot):
        return self.get_edge_positions_in_range_in_field(x=bot.pos.x, y=bot.pos.y, radius=self.config.move, field_radius=self.config.field_radius)

    def get_valid_cannons(self, bot):
        return self.get_positions_in_range(x=0, y=0, radius=self.config.field_radius)

    def get_valid_radars(self, bot):
        return self.get_positions_in_range(x=0, y=0, radius=self.config.field_radius)

    def get_positions_in_range(self, x=0, y=0, radius=1):
        for dx in xrange(-radius, radius+1):
            for dy in xrange(max(-radius, -dx-radius), min(radius, -dx+radius)+1):
                yield messages.Pos(dx+x, dy+y)

    def get_positions_in_range_wo_cur_pos(self, x=0, y=0, radius=1):
        for dx in xrange(-radius, radius+1):
            for dy in xrange(max(-radius, -dx-radius), min(radius, -dx+radius)+1):
                if dx != 0 and dy != 0: # Force move somewhere
                    yield messages.Pos(dx+x, dy+y)

    def get_edge_positions_in_range(self, x=0, y=0, radius=1):
        return self.circle(x, y, radius)

    def get_edge_positions_in_range_in_field(self, x=0, y=0, radius=1, field_radius=14):
        return self.circle_on_field(x, y, radius, field_radius)

    def east(self, x=0, y=0, n=1):
        return messages.Pos(x+n, y)
    def southeast(self, x=0, y=0, n=1):
        return messages.Pos(x, y+n)
    def southwest(self, x=0, y=0, n=1):
        return messages.Pos(x-n, y+n)
    def west(self, x=0, y=0, n=1):
        return messages.Pos(x-n, y)
    def northwest(self, x=0, y=0, n=1):
        return messages.Pos(x, y-n)
    def northeast(self, x=0, y=0, n=1):
        return messages.Pos(x+n, y-n)

    def pos_on_field(self, x=0, y=0, field_radius=14):
        # This is quite heavy operation, all field positions should be calculated only once
        field_points = self.get_positions_in_range(x=0, y=0, radius=field_radius)
        if messages.Pos(x,y) in field_points:
            return True
        return False

    def circle(self, x=0, y=0, radius=1):
        points = []
        cur = self.east(x, y, radius) # Start point
        for i in range(radius):
            points.append(cur)
            cur = self.southwest(cur.x, cur.y)
        for i in range(radius):
            points.append(cur)
            cur = self.west(cur.x, cur.y)
        for i in range(radius):
            points.append(cur)
            cur = self.northwest(cur.x, cur.y)
        for i in range(radius):
            points.append(cur)
            cur = self.northeast(cur.x, cur.y)
        for i in range(radius):
            points.append(cur)
            cur = self.east(cur.x, cur.y)
        for i in range(radius):
            points.append(cur)
            cur = self.southeast(cur.x, cur.y)
        return points

    def circle_on_field(self, x=0, y=0, radius=1, field_radius=14):
        points = []
        cur = self.east(x, y, radius) # Start point
        for i in range(radius):
            if self.pos_on_field(cur.x, cur.y, field_radius):
                points.append(cur)
            cur = self.southwest(cur.x, cur.y)
        for i in range(radius):
            if self.pos_on_field(cur.x, cur.y, field_radius):
                points.append(cur)
            cur = self.west(cur.x, cur.y)
        for i in range(radius):
            if self.pos_on_field(cur.x, cur.y, field_radius):
                points.append(cur)
            cur = self.northwest(cur.x, cur.y)
        for i in range(radius):
            if self.pos_on_field(cur.x, cur.y, field_radius):
                points.append(cur)
            cur = self.northeast(cur.x, cur.y)
        for i in range(radius):
            if self.pos_on_field(cur.x, cur.y, field_radius):
                points.append(cur)
            cur = self.east(cur.x, cur.y)
        for i in range(radius):
            if self.pos_on_field(cur.x, cur.y, field_radius):
                points.append(cur)
            cur = self.southeast(cur.x, cur.y)
        return points

    def move_random_max(self, bot):
            move_pos = random.choice(self.get_valid_edge_moves(bot))
            return actions.Move(bot_id=bot.bot_id,
                                x=move_pos[0],
                                y=move_pos[1])

    def move_random_max_in_field(self, bot):
            move_pos = random.choice(self.get_valid_edge_moves_in_field(bot))
            return actions.Move(bot_id=bot.bot_id,
                                x=move_pos[0],
                                y=move_pos[1])
    def move_random(self, bot):
            move_pos = random.choice(list(self.get_valid_moves(bot)))
            return actions.Move(bot_id=bot.bot_id,
                                x=move_pos.x,
                                y=move_pos.y)

    def move_random_force(self, bot):
            move_pos = random.choice(list(self.get_valid_moves_wo_cur_pos(bot)))
            return actions.Move(bot_id=bot.bot_id,
                                x=move_pos.x,
                                y=move_pos.y)

    def move_bot(self, bot, x, y):
            return actions.Move(bot_id=bot.bot_id,
                                x=x,
                                y=y)

    def cannon_random(self, bot):
            cannon_pos = random.choice(list(self.get_valid_cannons(bot)))
            return actions.Cannon(bot_id=bot.bot_id,
                                  x=cannon_pos.x,
                                  y=cannon_pos.y)
    def cannon(self, bot, x, y):
            return actions.Cannon(bot_id=bot.bot_id,
                                  x=x,
                                  y=y)

    def radar_random(self, bot):
            radar_pos = random.choice(list(self.get_valid_radars(bot)))
            return actions.Radar(bot_id=bot.bot_id,
                                 x=radar_pos.x,
                                 y=radar_pos.y)

    def radar(self, bot, x, y):
            return actions.Radar(bot_id=bot.bot_id,
                                  x=x,
                                  y=y)
