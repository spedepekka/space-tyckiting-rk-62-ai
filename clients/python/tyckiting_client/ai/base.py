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

    def get_valid_edge_moves(self, bot):
        return self.get_edge_positions_in_range(x=bot.pos.x, y=bot.pos.y, radius=self.config.move)

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
