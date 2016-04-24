import logging

from tyckiting_client import actions
from tyckiting_client.ai import base
from tyckiting_client.ai.strategies import scanning


'''
Rules:
Shoot at first target if available
Else scan random field
'''


class Ai(base.BaseAi):

    def __init__(self, team_id, config=None):
        super(Ai, self).__init__(team_id, config)
        self.scanning = scanning.RandomScanning(self.config)

    def move(self, bots, events):
        response = []
        targets = []

        for event in events:
            if event.event == 'radarEcho':
                targets.append(event.pos)
            elif event.event == 'see':
                targets.append(event.pos)
            else:
                logging.info('Unknown event %s', event.event)

        for bot in bots:
            if not bot.alive:
                continue
            if len(targets) > 0:
                target = targets[0]
                action = actions.Cannon(bot_id=bot.bot_id, x=target.x, y=target.y)
            else:
                scanPos = self.scanning.getScanPosition()
                action = actions.Radar(bot_id=bot.bot_id, x=scanPos.x, y=scanPos.y)
            response.append(action)
        return response
