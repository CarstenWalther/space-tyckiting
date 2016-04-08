import random
import logging

from tyckiting_client.ai import base
from tyckiting_client import actions

'''
Rules:
Shoot at first target if available
Else scan random field
'''


class Ai(base.BaseAi):

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
                scan_pos = random.choice(list(self.get_positions_in_range(radius=self.config.field_radius)))
                action = actions.Radar(bot_id=bot.bot_id, x=scan_pos.x, y=scan_pos.y)
            response.append(action)
        return response
