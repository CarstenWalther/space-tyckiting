import random

from tyckiting_client.ai import base
from tyckiting_client import actions
from tyckiting_client.ai.strategies.triangleShot import TriangleShot

'''
Rules:
If all bots alive and target available -> triangle shot
Else Move if in danger
Else shoot at first target if available
Else scan random field
'''

class Ai(base.BaseAi):

    def __init__(self, team_id, config=None):
        super(Ai, self).__init__(team_id, config)
        self.triShot = TriangleShot()

    def move(self, bots, events):
        response = []
        targetsPos = self.triShot.findTargets(events)
        if not targetsPos:
            targetsPos = self.getTargets(events)
        if self.livingBotCount(bots) == 3 and len(targetsPos) > 0:
            return self.triShot.shoot(bots, targetsPos[0])

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


