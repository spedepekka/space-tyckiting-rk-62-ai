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
        self.config = config #or {}
        self.print_game_config()

        # Calculate all the field points for later use
        self.field_points = set(self.get_positions_in_range(x=0, y=0, radius=self.config.field_radius))
        # Calculate all the radar points for later use
        self.optimal_radar_points = set(self.get_positions_in_range(x=0, y=0, radius=self.config.field_radius-self.config.radar))

    def print_game_config(self):
        """
        'field_radius': 14,
        'loop_time': 1000,
        'cannon': 1,
        'move': 2,
        'max_count': 200,
        'radar': 3, 'see': 2,
        'bots': 3,
        'start_hp': 10}
        """
        if self.config is not None:
            print "Game config"
            print self.config.__dict__
        else:
            print "Could not print game config, because it is None"

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

    def get_valid_radars_optimal_wall(self, bot):
        return self.optimal_radar_points

    # radars: list of Pos where already radared
    def get_valid_radars_optimal_wall_wo_overlap(self, radars):
        field = self.optimal_radar_points
        for r in radars:
            # self.config.radar*2 to avoid overlap
            dont_radar_here = self.get_positions_in_range(r.x, r.y, self.config.radar*2)
            field = field - set(dont_radar_here)
        return field

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
        if messages.Pos(x,y) in self.field_points:
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

    def radar_random_optimal_wall(self, bot):
            radar_pos = random.choice(list(self.get_valid_radars_optimal_wall(bot)))
            return actions.Radar(bot_id=bot.bot_id,
                                 x=radar_pos.x,
                                 y=radar_pos.y)

    def radar_random_optimal_wall_wo_overlap(self, bot, radars):
            radar_pos = random.choice(list(self.get_valid_radars_optimal_wall_wo_overlap(radars)))
            return actions.Radar(bot_id=bot.bot_id,
                                 x=radar_pos.x,
                                 y=radar_pos.y)

    def radar(self, bot, x, y):
            return actions.Radar(bot_id=bot.bot_id,
                                  x=x,
                                  y=y)

    # Return triangle points for shooting
    def triangle_points(self, x, y, radius=1):
        points = []
        # 2 different possibilities, random between them
        choise = random.randint(1,2)
        if choise == 1:
            points.append(self.northeast(x, y, radius))
            points.append(self.southeast(x, y, radius))
            points.append(self.west(x, y, radius))
        elif choise == 2:
            points.append(self.northwest(x, y, radius))
            points.append(self.southwest(x, y, radius))
            points.append(self.east(x, y, radius))
        else: # Fallback, should never happen, 3 same points to given coordinates
            for i in range(0,3):
                points.append(messages.Pos(x,y))
        return points
