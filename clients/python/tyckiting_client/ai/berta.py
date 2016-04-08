import random
import logging

from tyckiting_client.ai import base
from tyckiting_client import actions

'''
Rules:
Move if in danger
Else shoot at first target if available
Else scan random field
'''


class Ai(base.BaseAi):

    def move(self, bots, events):
        response = []
        targets = []
        endangered = set()

        for event in events:
            if event.event == 'radarEcho':
                targets.append(event.pos)
            elif event.event == 'see':
                targets.append(event.pos)
            elif event.event == 'detected':
                endangered.add(event.bot_id)
            elif event.event == 'damaged':
                pass
            elif event.event == 'hit':
                pass
            elif event.event == 'die':
                pass
            else:
                logging.info('Unknown event %s', event.event)

        print(endangered)

        for bot in bots:
            if not bot.alive:
                continue
            if bot.bot_id in endangered:
                mov_pos = random.choice(list(self.get_valid_moves(bot)))
                print(bot.pos)
                for pos in self.get_valid_moves(bot):
                    print('\t', pos)
                action = actions.Move(bot_id=bot.bot_id, x=mov_pos.x, y=mov_pos.y)
            elif len(targets) > 0:
                target = targets[0]
                action = actions.Cannon(bot_id=bot.bot_id, x=target.x, y=target.y)
            else:
                scan_pos = random.choice(list(self.get_positions_in_range(radius=self.config.field_radius)))
                action = actions.Radar(bot_id=bot.bot_id, x=scan_pos.x, y=scan_pos.y)
            response.append(action)
        return response
