"""
Hunter AI
"""

import random

from tyckiting_client.ai import base
from tyckiting_client import actions


class Ai(base.BaseAi):
    """
    Bots hunt for prey and then 1 follows and others shoot.
    """

    mode = "radar"
    last_radar_pos = None
    alive_bots = 0

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
                if e.event == "radarEcho":
                    self.last_radar_pos = e.pos
                    self.mode = "hunt"
                    found = True
                else:
                    print e.to_str()
            if not found:
                self.last_radar_pos = None
                self.mode = "radar"
        else:
            self.last_radar_pos = None
            self.mode = "radar"

        self.alive_bots = 0
        for i, bot in enumerate(bots):
            if not bot.alive:
                self.alive_bots += 1

        for i, bot in enumerate(bots, start=1):
            # If the bot is dead don't do anything
            if not bot.alive:
                continue

            # TODO: What if only one bot

            if self.mode == "radar":
                """
                action_handler = random.choice([self.move_random,
                                                self.cannon_random,
                                                self.radar_random])
                """
                response.append(self.radar_random(bot))
            else: # hunt
                if i == 1:
                    print "{} radaring".format(bot.bot_id)
                    response.append(self.radar(bot, self.last_radar_pos.x, self.last_radar_pos.y))
                else:
                    print "{} shooting to {}".format(bot.bot_id, self.last_radar_pos)
                    response.append(self.cannon(bot, self.last_radar_pos.x, self.last_radar_pos.y))

        return response

    def move_random(self, bot):
            move_pos = random.choice(list(self.get_valid_moves(bot)))
            return actions.Move(bot_id=bot.bot_id,
                                x=move_pos.x,
                                y=move_pos.y)

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
