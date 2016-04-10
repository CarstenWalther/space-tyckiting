import logging

from tyckiting_client import messages
from tyckiting_client import hexagon
from tyckiting_client import stats


class BaseAi:

    def __init__(self, team_id, config=None):
        """
        Initializes the AI, storing the configuration values as fields

        Args:
            team_id: Team identifier as an integer, shouldn't be needed
            config: Dictionary of game parameters
        """
        self.team_id = team_id
        self.config = config or {}

    def move(self, bots, events):
        """
        Perform bot actions, based on events from last round.

        This is the only method that needs to be implemented in custom AIs.

        Args:
            bots: List of bot states for own team
            events: List of events form previous round

        Returns:
            List of actions to perform this round.
        """

        raise NotImplementedError()

    def getEndangeredBots(self, events):
        endangered = set()
        for event in events:
            if event.event == 'see':
                endangered.add(event.source)
            elif event.event == 'detected':
                endangered.add(event.bot_id)
            elif event.event == 'damaged':
                pass
                #endangered.add(event.bot_id)
        if endangered:
            logging.info('endangered bots: %s', endangered)
        return endangered

    def getTargets(self, events):
        targets = []
        for event in events:
            if event.event == 'radarEcho':
                targets.append(event.pos)
            elif event.event == 'see':
                targets.append(event.pos)
        return targets

    def livingBotCount(self, bots):
        living = 0
        for bot in bots:
            if bot.alive:
                living += 1
        return living

    def get_valid_cannons(self, bot):
        return self.get_positions_in_range(x=0, y=0, radius=self.config.field_radius)

    def get_valid_radars(self, bot):
        return self.get_positions_in_range(x=0, y=0, radius=self.config.field_radius)

    def get_positions_in_range(self, x=0, y=0, radius=1):
        for dx in range(-radius, radius+1):
            for dy in range(max(-radius, -dx-radius), min(radius, -dx+radius)+1):
                yield messages.Pos(dx+x, dy+y)

    def coordinatesToPositions(self, coords):
        for coord in coords:
            yield messages.Pos(coord[0], coord[1])



