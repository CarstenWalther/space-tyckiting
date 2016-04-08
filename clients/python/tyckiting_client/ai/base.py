from tyckiting_client import messages
from tyckiting_client import hexagon


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

    def get_valid_moves(self, bot):
        coordinates = set()
        for radius in range(1, self.config.move + 1):
            coordinates |= hexagon.get_ring((bot.pos.x, bot.pos.y), radius)
        coordinates = hexagon.extractValidCoordinates(coordinates, self.config.field_radius)
        return self.coordinatesToPositions(coordinates)

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



