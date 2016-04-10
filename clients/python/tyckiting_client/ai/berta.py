import random

from tyckiting_client.ai import base
from tyckiting_client import actions

'''
Rules:
Move if in danger
Else shoot at first target if available
Else scan random field
'''


class Ai(base.BaseAi):

    def move(self, bots, events):
        response = []

        targetsPos = self.getTargets(events)
        endangered = self.getEndangeredBots(events)

        for bot in bots:
            if not bot.alive:
                continue
            if bot.bot_id in endangered:
                mov_pos = random.choice(list(self.get_valid_moves(bot)))
                action = actions.Move(bot_id=bot.bot_id, x=mov_pos.x, y=mov_pos.y)
            elif len(targetsPos) > 0:
                targetPos = targetsPos[0]
                action = actions.Cannon(bot_id=bot.bot_id, x=targetPos.x, y=targetPos.y)
            else:
                scan_pos = random.choice(list(self.get_positions_in_range(radius=self.config.field_radius)))
                action = actions.Radar(bot_id=bot.bot_id, x=scan_pos.x, y=scan_pos.y)
            response.append(action)
        return response
