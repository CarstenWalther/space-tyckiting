import random
import logging

from tyckiting_client.ai import base
from tyckiting_client import actions
from tyckiting_client.ai.strategies.triangleShot import TriangleShot
from tyckiting_client.ai.strategies import escaping
from tyckiting_client.ai.strategies import scanning
from tyckiting_client.ai.strategies import shooting

'''
Rules:
move if in danger
else spreadshooting if target available
else scan using statistical scanning

no triangle shot
'''

class Ai(base.BaseAi):

    def __init__(self, team_id, config=None):
        super(Ai, self).__init__(team_id, config)
        self.shooting = shooting.SpreadShooting(self.config)
        self.escaping = escaping.StraightDistance2Escaping(self.config)
        self.scanning = scanning.StatisticalScanning(self.config)

    def move(self, bots, events):
        response = []
        targetsPos = self.getTargets(events)
        endangered = self.getEndangeredBots(events)
        available = self.livingBotCount(bots) - len(endangered)

        logging.info('living:' + str(self.livingBotCount(bots)) + '\nendangered:' + str(endangered) + '\navailable:' + str(available))

        shooting = False
        if len(targetsPos) > 0 and available:
            shooting = True
            shotCoords = self.shooting.getShootPositions(targetsPos[0], available)
            logging.info('shooting request {} got {}'.format(available, shotCoords))
        elif available:
            scanCoords = self.scanning.getPossibleScanPositions(available)


        for bot in bots:
            if not bot.alive:
                continue
            if bot.bot_id in endangered:
                newPos = self.escaping.getMove(bot)
                action = actions.Move(bot_id=bot.bot_id, x=newPos.x, y=newPos.y)
            elif shooting:
                logging.info('shoot')
                shotCoord = shotCoords.pop()
                action = actions.Cannon(bot_id=bot.bot_id, x=shotCoord[0], y=shotCoord[1])
            else:
                scanCoord = scanCoords.pop()
                action = actions.Radar(bot_id=bot.bot_id, x=scanCoord[0], y=scanCoord[1])
            response.append(action)
        
        return response


