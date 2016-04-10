import random

from tyckiting_client.ai import base
from tyckiting_client import actions
from tyckiting_client.ai.strategies import escaping


'''
Rules:
Like Berta but moves straight distance 2
'''


class Ai(base.BaseAi):

    def __init__(self, team_id, config=None):
        super(Ai, self).__init__(team_id, config)
        self.escaping = escaping.StraightDistance2Escaping(self.config)

    def move(self, bots, events):
        response = []

        targetsPos = self.getTargets(events)
        endangered = self.getEndangeredBots(events)

        for bot in bots:
            if not bot.alive:
                continue
            if bot.bot_id in endangered:
                newPos = self.escaping.getMove(bot)
                action = actions.Move(bot_id=bot.bot_id, x=newPos.x, y=newPos.y)
            elif len(targetsPos) > 0:
                targetPos = targetsPos[0]
                action = actions.Cannon(bot_id=bot.bot_id, x=targetPos.x, y=targetPos.y)
            else:
                scanPos = random.choice(list(self.get_positions_in_range(radius=self.config.field_radius)))
                action = actions.Radar(bot_id=bot.bot_id, x=scanPos.x, y=scanPos.y)
            response.append(action)
        return response
