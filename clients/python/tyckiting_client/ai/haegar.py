import random

from tyckiting_client.ai import base
from tyckiting_client import actions
from tyckiting_client.ai.strategies.triangleShot import TriangleShot
from tyckiting_client.ai.strategies import escaping
from tyckiting_client.ai.strategies import scanning

'''
Rules:
like frida with DontOvershootScanning
'''

class Ai(base.BaseAi):

    def __init__(self, team_id, config=None):
        super(Ai, self).__init__(team_id, config)
        self.triShot = TriangleShot()
        self.escaping = escaping.StraightDistance2Escaping(self.config)
        self.scanning = scanning.StatisticalScanning(self.config)

    def move(self, bots, events):
        response = []
        targetsPos = self.triShot.findTargets(events)
        endangered = self.getEndangeredBots(events)

        if not targetsPos:
            targetsPos = self.getTargets(events)
        if self.livingBotCount(bots) == 3 and len(targetsPos) > 0 and not endangered:
            return self.triShot.shoot(bots, targetsPos[0])

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
                scanPos = self.scanning.getScanPosition()
                action = actions.Radar(bot_id=bot.bot_id, x=scanPos.x, y=scanPos.y)
            response.append(action)
        return response


