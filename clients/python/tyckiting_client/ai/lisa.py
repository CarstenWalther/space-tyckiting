import random

from tyckiting_client.ai import base
from tyckiting_client import actions
from tyckiting_client import hexagon
from tyckiting_client.ai.strategies.triangleShot import TriangleShot
from tyckiting_client.ai.strategies import escaping
from tyckiting_client.ai.strategies import scanning
from tyckiting_client.ai.strategies import shooting

'''
Rules:
move if in danger
- also in danger if close to target of mass shooting :O
else spreadshooting if target available
- select target that is the furthest away from all own bots
else scan using statistical scanning

no triangle shot
'''

class Ai(base.BaseAi):

    def __init__(self, team_id, config=None):
        super(Ai, self).__init__(team_id, config)
        self.shooting = shooting.SpreadShooting(self.config)
        self.escaping = escaping.StraightDistance2Escaping(self.config)
        self.scanning = scanning.StatisticalScanning(self.config)
        self.avoid_selfhit = escaping.AvoidSelfhit(self.config)

    def distance(self, pos1, pos2):
    	return ((pos1.x-pos2.x)**2 + (pos1.y-pos2.y)**2)**0.5

    def avgDistanceToPos(self, pos, posList):
    	distances = [self.distance(aPos, pos) for aPos in posList]
    	return sum(distances)/len(distances)

    def move(self, bots, events):
        response = []
        
        targetsPos = self.getTargets(events)
        target = None
        if len(targetsPos) == 1:
            target = targetsPos[0]
        elif len(targetsPos) > 1:
            # extract furthest target
            ownBotsPositions = [bot.pos for bot in bots]
            targetDistanceToOwnBots = [(self.avgDistanceToPos(tPos, ownBotsPositions), tPos) for tPos in targetsPos]
            target = max(targetDistanceToOwnBots)[1]

        endangered = self.getEndangeredBots(events)
        selfhit = set()
        #todo: improve
        if target:
            dangerousTiles = hexagon.getCircle(self.config.cannon + 2, target.x, target.y)
            ownBotsAboutToSelfHit = [bot.bot_id for bot in bots if (bot.pos.x, bot.pos.y) in dangerousTiles]
            selfhit = set(ownBotsAboutToSelfHit)

        available = self.livingBotCount(bots) - len(endangered) - len(selfhit)

        shooting = False
        if len(targetsPos) > 0 and available:
            shooting = True

            shotCoords = self.shooting.getShootPositions(target, available)
        else:
            scanCoords = self.scanning.getPossibleScanPositions(available)

        for bot in bots:
            if not bot.alive:
                continue
            if bot.bot_id in selfhit:
                self.avoid_selfhit.setEnemy(target)
                newPos = self.avoid_selfhit.getMove(self.config)
                action = actions.Move(bot_id=bot.bot_id, x=newPos.x, y=newPos.y)

            elif bot.bot_id in endangered:
                newPos = self.escaping.getMove(bot)
                action = actions.Move(bot_id=bot.bot_id, x=newPos.x, y=newPos.y)

            elif shooting:
                shotCoord = shotCoords.pop()
                action = actions.Cannon(bot_id=bot.bot_id, x=shotCoord[0], y=shotCoord[1])
            else:
                scanCoord = scanCoords.pop()
                action = actions.Radar(bot_id=bot.bot_id, x=scanCoord[0], y=scanCoord[1])
            response.append(action)
        
        return response


