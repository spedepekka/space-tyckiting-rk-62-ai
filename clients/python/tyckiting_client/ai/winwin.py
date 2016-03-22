"""
The one after goodradar
"""

import random
import copy

from tyckiting_client.ai import base
from tyckiting_client import actions
from tyckiting_client import messages

class Round(object):
    round_no = 0
    events = []
    bots = []
    triangle_shot = None # Middle point of triangle if shot

    def __init__(self, round_no=0):
        self.round_no = round_no
        self.events = []
        self.bots = []
        self.triangle_shot = None

    def print_bots(self):
        for bot in self.bots:
            print "Bot: {}".format(bot.__dict__)

    def print_events(self):
        for e in self.events:
            print "Event: {}".format(e.__dict__)

    def get_bot_shoot_coordinate(self, bot_id):
        for bot in self.bots:
            if bot.bot_id == bot_id:
                return bot.shoot
        return None # Should not happen

class Ai(base.BaseAi):
    """
    Bots hunt for prey and then 1 follows and others shoot.
    """

    mode = "radar"
    last_radar_pos = None
    alive_bots_no = 0
    attacking_bots_no = 0
    round_no = -1
    rounds = []
    radar_these = [] # Interesting points to radar
    expecting_direct_hit = False
    enemy_can_flank = True
    enemy_can_flank_counter = 0
    enemy_can_flank_counter_limit = 0
    tracker = None

    def get_last_round(self):
        if self.round_no >= 1:
            return self.rounds[-1]
        return Round() # On first round return empty round
    
    def add_radar_this(self, pos):
        print "Try to add radar {}".format(pos)
        print "Radars: {}".format(self.radar_these)
        if pos not in self.radar_these:
            print "Added"
            self.radar_these.append(pos)
        else:
            print "NOT added"

    def move(self, bots, events):
        """
        Move the bot to a random legal positon.

        Args:
            bots: List of bot states for own team
            events: List of events form previous round

        Returns:
            List of actions to perform this round.
        """

        response = []
        
        self.round_no += 1
        cur_round = Round(self.round_no)
        cur_round.events = events
        self.increase_jradar_values()

        found = False
        hit = False
        my_bot_ids = []
        for bot in bots:
            my_bot_ids.append(bot.bot_id)

        if len(events) >= 1:
            for e in events:
                if e.event == "hit":
                    if e.bot_id not in my_bot_ids: # Don't count friendly fire
                        print "HIT: Our bot {} hit to bot {}".format(e.source, e.bot_id)
                        hit = True
                        # If we hit don't loose the bot we hit. Radar the shoot point later.
                        # Default game config and with 1 move radar should catch the bot.
                        radar_this = self.get_last_round().get_bot_shoot_coordinate(e.source)
                        print "Interesting point to radar {}".format(radar_this)
                        #self.add_radar_this(radar_this)
                        self.tracker = radar_this
                        self.mode = "hunt"
                        self.last_radar_pos = radar_this
                        found = True
                    else:
                        print "Friendlyfire: Bot {} shot bot {}".format(e.source, e.bot_id)
                elif e.event == "die":
                    print "DIE: Bot {} died".format(e.bot_id)
                elif e.event == "radarEcho":
                    print "RADARECHO {}".format(e.pos)
                    self.last_radar_pos = e.pos
                    self.mode = "hunt"
                    found = True
                elif e.event == "see":
                    print "SEE"
                    for bot in bots:
                        if bot.bot_id == e.bot_id:
                            print "set bot {} as detected".format(bot.bot_id)
                            bot.detected = True
                        # Hack to radar seen enemies
                        self.add_radar_this(messages.Pos(e.pos.x, e.pos.y))
                elif e.event == "detected":
                    print "DETECTED"
                    for bot in bots:
                        if bot.bot_id == e.bot_id:
                            print "set bot {} as detected".format(bot.bot_id)
                            bot.detected = True
                elif e.event == "damaged":
                    print "DAMAGED"
                    for bot in bots:
                        if bot.bot_id == e.bot_id:
                            print "set bot {} as detected".format(bot.bot_id)
                            bot.detected = True
                elif e.event == "move":
                    print "MOVE"
                elif e.event == "end":
                    print "END"
                elif e.event == "noaction":
                    print "NOACTION"
                else:
                    print "WARNING: Unknown event"

                #{'name': u'hunter 1', 'hp': 10, 'pos': Pos(x=6, y=-12), 'alive': True, 'team_id': 0, 'detected': False, 'bot_id': 0}
                print "Event: {}".format(e.__dict__)

            if not found:
                self.last_radar_pos = None
                self.mode = "radar"
        else:
            self.last_radar_pos = None
            self.mode = "radar"

        # If the last triangle shot missed try to radar the last triangle middle
        # point to find the enemy again
        if self.get_last_round().triangle_shot is not None and not hit:
            self.add_radar_this(self.get_last_round().triangle_shot)

        if self.expecting_direct_hit:
            if not hit:
                self.enemy_can_flank_counter += 1
                if self.enemy_can_flank_counter >= self.enemy_can_flank_counter_limit:
                    self.enemy_can_flank = True
            else:
                self.enemy_can_flank_counter = 0
                self.expecting_direct_hit = False

        # Preparations
        self.alive_bots_no = 0
        self.attacking_bots_no = 0
        for i, bot in enumerate(bots):
            print "Bot: {}".format(bot.__dict__)
            if bot.alive:
                self.alive_bots_no += 1
                if not bot.detected:
                    self.attacking_bots_no += 1

        print "{} bots alive and {} will attack".format(self.alive_bots_no, self.attacking_bots_no)

        radars = []
        radaring_bot = False
        triangle_points = []

        for i, bot in enumerate(bots, start=1):
            # If the bot is dead don't do anything
            if bot.alive:
                # Always flank first
                if bot.detected:
                    print "{} PANIC".format(bot.bot_id)
                    move_pos = self.move_random_max_in_field(bot)
                    response.append(move_pos)
                    bot.move = messages.Pos(move_pos.x, move_pos.y)
                else:
                    if self.mode == "radar":
                        print "     {} radaring".format(bot.bot_id)
                        radar_action = None
                        if len(self.radar_these) > 0:
                            print "POP: {}".format(self.radar_these)
                            radar_pos = self.radar_these.pop(0) # FIFO
                            radar_action = actions.Radar(bot_id=bot.bot_id, x=radar_pos.x, y=radar_pos.y)
                        else:
                            # Go through the minimum number of optimal radars at first (Lasse's radar)
                            if len(self.min_optimal_radars) >= 1:
                                min_point = self.min_optimal_radars.pop()
                                print "Pop min radar point {} number of points left {}".format(min_point, len(self.min_optimal_radars))
                                radar_action = actions.Radar(bot_id=bot.bot_id, x=min_point.x, y=min_point.y)
                            # Then start radaring on random
                            else:
                                #radar_action = self.radar_random_optimal_wall_wo_overlap(bot, radars)
                                radar_to = self.get_single_biggest_jradar_points()
                                radar_action = self.jradar(bot, radar_to[0].x, radar_to[0].y)
                                print "jradar to {},{}. The biggest value is {}".format(radar_action.x, radar_action.y, radar_to[1])
                        radars.append(messages.Pos(radar_action.x, radar_action.y))
                        response.append(radar_action)
                        bot.radar = messages.Pos(radar_action.x, radar_action.y)
                    else: # hunt
                        print "     HUNTING"
                        if not radaring_bot and hit:
                            radaring_bot = True
                            print "{} radaring".format(bot.bot_id)
                            radar_pos = self.jradar(bot, self.last_radar_pos.x, self.last_radar_pos.y)
                            response.append(radar_pos)
                            bot.radar = messages.Pos(radar_pos.x, radar_pos.y)
                        else:
                            #if self.attacking_bots_no == 3 or self.enemy_can_flank:
                            if len(triangle_points) == 0:
                                triangle_points = self.triangle_points(self.last_radar_pos.x, self.last_radar_pos.y)
                            point_to_shoot = triangle_points[i % 3]
                            print "{} triangle shooting to {}".format(bot.bot_id, point_to_shoot)
                            bot.shoot = point_to_shoot
                            cur_round.triangle_shot = messages.Pos(self.last_radar_pos.x, self.last_radar_pos.y)
                            response.append(self.cannon(bot, point_to_shoot.x, point_to_shoot.y))
                        """
                        else: # Direct shot
                            # One bot always radars
                            if not radaring_bot:
                                radaring_bot = True
                                print "{} radaring".format(bot.bot_id)
                                radar_pos = self.jradar(bot, self.last_radar_pos.x, self.last_radar_pos.y)
                                response.append(radar_pos)
                                bot.radar = messages.Pos(radar_pos.x, radar_pos.y)
                            else:
                                self.expecting_direct_hit = True
                                print "{} shooting to {}".format(bot.bot_id, self.last_radar_pos)
                                cannon_pos = self.cannon(bot, self.last_radar_pos.x, self.last_radar_pos.y)
                                response.append(cannon_pos)
                                bot.shoot = messages.Pos(cannon_pos.x, cannon_pos.y)
                        """

            cur_round.bots.append(bot)


        print "Round {} actions and stuff".format(self.round_no)
        print cur_round.__dict__
        cur_round.print_bots()
        self.rounds.append(cur_round)

        return response

