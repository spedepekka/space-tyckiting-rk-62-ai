"""
Hunter AI
"""

import random

from tyckiting_client.ai import base
from tyckiting_client import actions
from tyckiting_client import messages


class Ai(base.BaseAi):
    """
    Bots hunt for prey and then 1 follows and others shoot.
    """

    mode = "radar"
    last_radar_pos = None
    alive_bots = 0
    triangle_shot = True

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

        found = False

        if len(events) >= 1:
            for e in events:
                if e.event == "hit":
                    print "HIT"
                elif e.event == "die":
                    print "DIE"
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

                print e.__dict__

            if not found:
                self.last_radar_pos = None
                self.mode = "radar"
        else:
            self.last_radar_pos = None
            self.mode = "radar"

        self.alive_bots = 0
        for i, bot in enumerate(bots):
            print bot.__dict__
            if not bot.alive:
                self.alive_bots += 1

        radars = []
        radaring_bot = False
        triangle_points = []

        if self.triangle_shot and self.mode != "radar":
            print "Ready to triangle shot"
            triangle_points = self.triangle_points(self.last_radar_pos.x, self.last_radar_pos.y)

        for i, bot in enumerate(bots, start=1):
            print "Resolving bot {}".format(bot.bot_id)
            # If the bot is dead don't do anything
            if not bot.alive:
                continue

            if bot.detected:
                # If the bot is panicking it won't shoot or radar
                print "{} PANIC".format(bot.bot_id)
                response.append(self.move_random_max_in_field(bot))
                continue

            # TODO: What if only one bot

            if self.mode == "radar":
                print "{} radaring".format(bot.bot_id)
                radar_action = self.radar_random_optimal_wall_wo_overlap(bot, radars)
                radars.append(messages.Pos(radar_action.x, radar_action.y))
                response.append(radar_action)
            else: # hunt
                if self.triangle_shot:
                    point_to_shoot = triangle_points[i % 3]
                    print "{} triangle shooting to {}".format(bot.bot_id, point_to_shoot)
                    response.append(self.cannon(bot, point_to_shoot.x, point_to_shoot.y))
                else:
                    # One bot always radars
                    if not radaring_bot:
                        radaring_bot = True
                        print "{} radaring".format(bot.bot_id)
                        response.append(self.radar(bot, self.last_radar_pos.x, self.last_radar_pos.y))
                    else:
                        print "{} shooting to {}".format(bot.bot_id, self.last_radar_pos)
                        response.append(self.cannon(bot, self.last_radar_pos.x, self.last_radar_pos.y))

        return response

