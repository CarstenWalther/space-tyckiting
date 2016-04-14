import logging
from tyckiting_client.utilities import *

from tyckiting_client import messages
from tyckiting_client import hexagon
from tyckiting_client import stats

import tyckiting_client.notifications as notifications

from tyckiting_client.utilities import *

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
        self.stats = None

    def notifyAboutNewRound(self, bots, events):
        data = {
            'bots': bots,
            'events': events
        }
        notification = notifications.Notification(notifications.ID_START_ROUND_NOTIFICATION, data)
        notifications.defaultNotificationCenter.send(notification)

    def notifyAboutTakenActions(self, actions):
        data = {
            'actions': actions
        }
        notification = notifications.Notification(notifications.ID_END_ROUND_NOTIFICATION, data)
        notifications.defaultNotificationCenter.send(notification)

    @log_execution_time
    def decide(self, bots, events):
        self.logEvents(events)
        self.notifyAboutNewRound(bots, events)
        response = self.move(bots, events)
        self.notifyAboutTakenActions(response)
        self.logActions(response)
        return response

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
                self.addIfNotDead(endangered, event.source, events)
            elif event.event == 'detected':
                endangered.add(event.bot_id)
            elif event.event == 'damaged':
                #endangered.add(event.bot_id)
                pass
        return endangered

    def addIfNotDead(self, endangeredBots, botId, events):
        dead = False
        for event in events:
            if event.event == 'die' and event.bot_id == botId:
                dead = True
                break
        if not dead:
            endangeredBots.add(botId)

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

    def logEvents(self, events):
        for event in events:
            self.stats.analyzeEvent(event)

    def logActions(self, actions):
        for action in actions:
            self.stats.analyzeAction(action)

    def startLogging(self, teamBots, teamName, enemyName):
        teamBotIds = [bot.bot_id for bot in teamBots]
        self.stats = stats.GameStats(teamBotIds, teamName, enemyName)

    def finishLogging(self, result):
        logging.info(self.stats)
        log_execution_time_stats()
        self.stats.writeToFile(result)
