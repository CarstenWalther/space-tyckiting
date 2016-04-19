import logging

from tyckiting_client.ai import base
from tyckiting_client import actions
from tyckiting_client import hexagon
from tyckiting_client.ai.strategies import escaping
from tyckiting_client.ai.strategies import scanning
from tyckiting_client.ai.strategies import shooting
from tyckiting_client.ai.strategies import tracking

'''
Rules:
like mona but only perma scans if there are more than one bot available
uses enemy tracking
'''

class Ai(base.BaseAi):

    def __init__(self, team_id, config=None):
        super(Ai, self).__init__(team_id, config)
        self.escaping = escaping.StraightDistance2Escaping(self.config)
        self.scanning = scanning.StatisticalScanning(self.config)
        self.tracking = tracking.Tracker(tracking.STRAIGHT_DISTANCE2_PATTERN)

    def move(self, bots, events):
        response = []
        endangered = self.getEndangeredBots(events)
        livingCount = self.livingBotCount(bots)
        available = livingCount - len(endangered)
        target = self.tracking.getTarget()

        print(self.tracking.movementCounter)

        pendingTrackScan = False
        if target and available >= 2:
            pendingTrackScan = True
            available -= 1

        shooting = True
        shootCoords = self.tracking.getShootCoordinates(available)
        if not shootCoords:
            shooting = False
            scanCoords = self.scanning.getPossibleScanPositions(available)

        for bot in bots:
            if not bot.alive:
                continue
            if bot.bot_id in endangered:
                newPos = self.escaping.getMove(bot)
                action = actions.Move(bot_id=bot.bot_id, x=newPos.x, y=newPos.y)
            elif pendingTrackScan:
                action = actions.Radar(bot_id=bot.bot_id, x=target[0], y=target[1])
                pendingTrackScan = False
            elif shooting:
                shootCoord = shootCoords.pop()
                action = actions.Cannon(bot_id=bot.bot_id, x=shootCoord[0], y=shootCoord[1])
            else:
                scanCoord = scanCoords.pop()
                action = actions.Radar(bot_id=bot.bot_id, x=scanCoord[0], y=scanCoord[1])
            response.append(action)
        
        return response

