import logging

from tyckiting_client.ai import base
from tyckiting_client import actions
from tyckiting_client import hexagon
from tyckiting_client.ai.strategies import escaping
from tyckiting_client.ai.strategies import scanning
from tyckiting_client.ai.strategies import shooting

'''
Rules:
continuously tracks one target by scanning it each round
only use continuously tracking if you have >1 bots
beside that:
move if in danger
else shoot if target available
else scan
'''

class Ai(base.BaseAi):

    def __init__(self, team_id, config=None):
        super(Ai, self).__init__(team_id, config)
        self.shooting = shooting.SpreadShooting(self.config)
        self.escaping = escaping.StraightDistance2Escaping(self.config)
        self.scanning = scanning.StatisticalScanning(self.config)
        self.targetPos = None

    def move(self, bots, events):
        response = []
        targetsPos = self.getTargets(events)
        endangered = self.getEndangeredBots(events)
        livingCount = self.livingBotCount(bots)
        available = livingCount - len(endangered)
        self.targetPos = self.determineTrackedTarget(targetsPos)

        pendingTrackScan = False
        if self.targetPos and livingCount > 1 and available:
            pendingTrackScan = True
            available -= 1

        shooting = False
        if self.targetPos and available:
            shooting = True
            shotCoords = self.shooting.getShootPositions(self.targetPos, available)
        elif available:
            scanCoords = self.scanning.getPossibleScanPositions(available)

        for bot in bots:
            if not bot.alive:
                continue
            if bot.bot_id in endangered:
                newPos = self.escaping.getMove(bot)
                action = actions.Move(bot_id=bot.bot_id, x=newPos.x, y=newPos.y)
            elif pendingTrackScan:
                action = actions.Radar(bot_id=bot.bot_id, x=self.targetPos[0], y=self.targetPos[1])
                pendingTrackScan = False
            elif shooting:
                shotCoord = shotCoords.pop()
                action = actions.Cannon(bot_id=bot.bot_id, x=shotCoord[0], y=shotCoord[1])
            else:
                scanCoord = scanCoords.pop()
                action = actions.Radar(bot_id=bot.bot_id, x=scanCoord[0], y=scanCoord[1])
            response.append(action)
        
        return response

    def determineTrackedTarget(self, targetsPos):
        if len(targetsPos) == 0:
            return None
        validPositions = hexagon.extractValidCoordinates(targetsPos, self.config.move)
        if len(validPositions) > 0:
            return validPositions.pop()
        else:
            return targetsPos.pop()

