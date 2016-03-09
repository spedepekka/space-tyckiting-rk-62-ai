"""
Hunter AI
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

    def __init__(self, round_no):
        self.round_no = round_no
        self.events = []
        self.bots = []

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
    alive_bots = 0
    game_config_printed = False
    round_no = -1
    rounds = []

    def get_last_round(self):
        if self.round_no >= 1:
            return rounds[-1]

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
        if not self.game_config_printed:
            print "Game config"
            print self.config.__dict__
        self.game_config_printed = True

    def move(self, bots, events):
        """
        Move the bot to a random legal positon.

        Args:
            bots: List of bot states for own team
            events: List of events form previous round

        Returns:
            List of actions to perform this round.
        """
        self.print_game_config()

        response = []
        
        self.round_no += 1
        cur_round = Round(self.round_no)
        cur_round.events = events

        found = False

        if len(events) >= 1:
            for e in events:
                if e.event == "hit":
                    print "HIT: Our bot {} hit to bot {}".format(e.source, e.bot_id)
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

        self.alive_bots = 0
        for i, bot in enumerate(bots):
            print "Bot: {}".format(bot.__dict__)
            if not bot.alive:
                self.alive_bots += 1

        radars = []
        radaring_bot = False

        for i, bot in enumerate(bots, start=1):
            # If the bot is dead don't do anything
            if bot.alive:
                if bot.detected:
                    print "{} PANIC".format(bot.bot_id)
                    move_pos = self.move_random_max_in_field(bot)
                    response.append(move_pos)
                    bot.move(move_pos.x, move_pos.y)
                    continue

                # TODO: What if only one bot

                if self.mode == "radar":
                    print "{} radaring".format(bot.bot_id)
                    radar_action = self.radar_random_optimal_wall_wo_overlap(bot, radars)
                    radars.append(messages.Pos(radar_action.x, radar_action.y))
                    response.append(radar_action)
                    bot.radar = messages.Pos(radar_action.x, radar_action.y)
                else: # hunt
                    # One bot always radars
                    if not radaring_bot:
                        radaring_bot = True
                        print "{} radaring".format(bot.bot_id)
                        radar_pos = self.radar(bot, self.last_radar_pos.x, self.last_radar_pos.y)
                        response.append(radar_pos)
                        bot.radar = messages.Pos(radar_pos.x, radar_pos.y)
                    else:
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

