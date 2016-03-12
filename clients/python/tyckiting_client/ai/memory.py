"""
The one after hunter with some memory
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

    def __init__(self, round_no):
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
    enemy_can_flank = False
    enemy_can_flank_counter = 0
    enemy_can_flank_counter_limit = 3

    def get_last_round(self):
        if self.round_no >= 1:
            return rounds[-1]

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

        found = False
        hit = False

        if len(events) >= 1:
            for e in events:
                if e.event == "hit":
                    print "HIT: Our bot {} hit to bot {}".format(e.source, e.bot_id)
                    hit = True
                elif e.event == "die":
                    print "DIE: Bot {} died".format(e.bot_id)
                elif e.event == "radarEcho":
                    print "RADARECHO"
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
                        self.radar_these.append(messages.Pos(e.pos.x, e.pos.y))
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
                        print "{} radaring".format(bot.bot_id)
                        radar_action = None
                        if len(self.radar_these) > 0:
                            print "POP: {}".format(self.radar_these)
                            radar_pos = self.radar_these.pop(0) # FIFO
                            radar_action = actions.Radar(bot_id=bot.bot_id, x=radar_pos.x, y=radar_pos.y)
                        else:
                            radar_action = self.radar_random_optimal_wall_wo_overlap(bot, radars)
                        radars.append(messages.Pos(radar_action.x, radar_action.y))
                        response.append(radar_action)
                        bot.radar = messages.Pos(radar_action.x, radar_action.y)
                    else: # hunt
                        if self.attacking_bots_no == 3 or self.enemy_can_flank:
                            if len(triangle_points) == 0:
                                if self.enemy_can_flank and self.attacking_bots_no != 3:
                                    triangle_points = self.triangle_points(self.last_radar_pos.x, self.last_radar_pos.y, radius=1)
                                else:
                                    triangle_points = self.triangle_points(self.last_radar_pos.x, self.last_radar_pos.y)
                            point_to_shoot = triangle_points[i % 3]
                            print "{} triangle shooting to {}".format(bot.bot_id, point_to_shoot)
                            bot.shoot = point_to_shoot
                            cur_round.triangle_shot = messages.Pos(self.last_radar_pos.x, self.last_radar_pos.y)
                            radar_this = messages.Pos(self.last_radar_pos.x, self.last_radar_pos.y)
                            if radar_this not in self.radar_these:
                                self.radar_these.append(radar_this)
                            response.append(self.cannon(bot, point_to_shoot.x, point_to_shoot.y))
                        else: # Direct shot
                            # One bot always radars
                            if not radaring_bot:
                                radaring_bot = True
                                print "{} radaring".format(bot.bot_id)
                                radar_pos = self.radar(bot, self.last_radar_pos.x, self.last_radar_pos.y)
                                response.append(radar_pos)
                                bot.radar = messages.Pos(radar_pos.x, radar_pos.y)
                            else:
                                self.expecting_direct_hit = True
                                print "{} shooting to {}".format(bot.bot_id, self.last_radar_pos)
                                cannon_pos = self.cannon(bot, self.last_radar_pos.x, self.last_radar_pos.y)
                                response.append(cannon_pos)
                                bot.shoot = messages.Pos(cannon_pos.x, cannon_pos.y)

            cur_round.bots.append(bot)

        print "Round {} actions and stuff".format(self.round_no)
        print cur_round.__dict__
        cur_round.print_bots()
        self.rounds.append(cur_round)

        return response

