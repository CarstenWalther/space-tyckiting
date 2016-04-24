from tyckiting_client.ai import base
from tyckiting_client import actions
from tyckiting_client.ai.strategies import pipelineEscaping
from tyckiting_client.ai.strategies import scanning
from tyckiting_client.ai.strategies import uncertainTracking

'''
Rules:
orania with uncertain tracking
'''

class Ai(base.BaseAi):

    def __init__(self, team_id, config=None):
        super(Ai, self).__init__(team_id, config)
        self.escaping = pipelineEscaping.PipelineEscapingAdvanced(self.config)
        self.scanning = scanning.StatisticalScanning(self.config)
        self.tracking = uncertainTracking.UncertainTracker(uncertainTracking.BALANCED_PATTERN)

    def move(self, bots, events):
        response = []
        endangered = self.getEndangeredBots(events)
        livingCount = self.livingBotCount(bots)
        available = livingCount - len(endangered)
        target = self.tracking.getTarget()

        positionsNextRound = self.doPositioning(endangered, response, bots, target)

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
            if bot.bot_id in endangered:
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
