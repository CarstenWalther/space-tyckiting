import logging
import random

from tyckiting_client import hexagon
from tyckiting_client.messages import Pos
from tyckiting_client.ai.strategies import escaping

class PipelineEscaping(escaping.Escaping):

	def __init__(self, config):
		self.config = config
		self.avoid_selfhit = escaping.AvoidSelfhit(self.config)
		self.avoid_walls = escaping.AvoidWallsAdvanced(self.config)
		self.straight = escaping.StraightDistance2Escaping(self.config)
		self.curved = escaping.CurvedDistance2Escaping(self.config)
		self.avoid_grouping = escaping.AvoidGrouping(self.config)

	def getMove(self, bot, own_bots, target):
		source = ""

		found = False

		if target and hexagon.distance(bot.pos, target) < 4:
			self.avoid_selfhit.setEnemy(target)
			coords = self.avoid_selfhit.getPossibleMoves(bot)
			if len(coords) != 0:
				found = True

			source = "avoid_selfhit"
		if not found and hexagon.distance(bot.pos, (0,0)) > 11:
			coords = self.avoid_walls.getPossibleMoves(bot)
			if len(coords) != 0:
				found = True
			source = "avoid_walls"
		if not found:
			distance_to_team = 32
			bots = own_bots.copy()
			bots.remove(bot)
			for own_bot in bots:
				if hexagon.distance(own_bot.pos, bot.pos) < distance_to_team:
					distance_to_team = hexagon.distance(own_bot.pos, bot.pos)

			if distance_to_team < 4:
				self.avoid_grouping.setTeammates(bots)
				coords = self.avoid_grouping.getPossibleMoves(bot)
				if len(coords) != 0:
					found = True
				source = "avoid_grouping"

		if not found:
				c1 = self.straight.getPossibleMoves(bot)
				c2 = self.curved.getPossibleMoves(bot)
				coords = c1 | c2
				source = "two random"
		logging.info('Source is %s', source)


		coord = random.choice(list(coords))
		pos = Pos(coord[0], coord[1])
		logging.info('Move %d from %s to %s', bot.bot_id, bot.pos, pos)
		return pos

class PipelineEscapingAdvanced(PipelineEscaping):

	def getMove(self, bot, own_bots, target):
		source = ""
		final_coords = set()
		found = False

		if target and hexagon.distance(bot.pos, target) < 5:
			self.avoid_selfhit.setEnemy(target)
			coords = self.avoid_selfhit.getPossibleMoves(bot)
			final_coords = coords
			source += "avoid_selfhit; "

		if hexagon.distance(bot.pos, (0,0)) > 10:
			coords = self.avoid_walls.getPossibleMoves(bot)
			if len(final_coords) == 0:
				final_coords = coords
				source += "avoid_walls; "
			else:
				new_coords = final_coords & coords
				if len(new_coords) > 0:
					final_coords = new_coords
					source += "avoid_walls; "

		distance_to_team = 32
		bots = own_bots.copy()
		bots.remove(bot)
		for own_bot in bots:
			if hexagon.distance(own_bot.pos, bot.pos) < distance_to_team:
				distance_to_team = hexagon.distance(own_bot.pos, bot.pos)
			if distance_to_team < 5:
				self.avoid_grouping.setTeammates(bots)
				coords = self.avoid_grouping.getPossibleMoves(bot)
				if len(final_coords) == 0:
					final_coords = coords
					source += "avoid_grouping; "
				else:
					new_coords = final_coords & coords
					if len(new_coords) > 0:
						final_coords = new_coords
						source += "avoid_grouping; "

		if len(final_coords) == 0:
				c1 = self.straight.getPossibleMoves(bot)
				c2 = self.curved.getPossibleMoves(bot)
				final_coords = c1 | c2
				source += "two random; "
		logging.info('Source is %s', source)


		coord = random.choice(list(final_coords))
		pos = Pos(coord[0], coord[1])
		logging.info('Move %d from %s to %s', bot.bot_id, bot.pos, pos)
		return pos