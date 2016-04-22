import logging
import random

from tyckiting_client.ai import base
from tyckiting_client import actions
from tyckiting_client import hexagon
from tyckiting_client.ai.strategies import escaping
from tyckiting_client.ai.strategies import scanning
from tyckiting_client.ai.strategies import shooting
from tyckiting_client.ai.strategies import uncertainTracking

'''
Rules:
like robin but in certain situations endangered bots stay and do an other action
'''

STAY_PROB = 0.15

class Ai(base.BaseAi):

    def __init__(self, team_id, config=None):
        super(Ai, self).__init__(team_id, config)
        self.escaping = escaping.PipelineEscapingAdvanced(self.config)
        self.scanning = scanning.StatisticalScanning(self.config)
        self.tracking = uncertainTracking.UncertainTracker(uncertainTracking.BALANCED_PATTERN)

    def move(self, bots, events):
        response = []
        endangered = self.getEndangeredBots(events)
        livingCount = self.livingBotCount(bots)
        target = self.tracking.getTarget()

        botsToMove = []
        for endangeredBot in endangered:
            if random.uniform(0,1) > STAY_PROB:
                botsToMove.append(endangeredBot)

        available = livingCount - len(botsToMove)

        positionsNextRound = self.doPositioning(botsToMove, response, bots, target)

        pendingTrackScan = False
        if target and available >= 2:
            pendingTrackScan = True
            available -= 1

        shooting = True
        shootCoords = self.tracking.getShootCoordinates(available, positionsNextRound)
        if not shootCoords:
            shooting = False
            scanCoords = self.scanning.getPossibleScanPositions(available)

        for bot in bots:
            if not bot.alive:
                continue
            if bot.bot_id in botsToMove:
                continue
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

    def doPositioning(self, botsToMove, response, bots, target):
        positions = []
        for bot in bots:
            if not bot.alive:
                continue
            if bot.bot_id in botsToMove:
                newPos = self.escaping.getMove(bot, bots, target)
                action = actions.Move(bot_id=bot.bot_id, x=newPos.x, y=newPos.y)
                response.append(action)
                positions.append(newPos)
            else:
                positions.append(bot.pos)
        return positions

