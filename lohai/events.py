import enum
import logging


logger = logging.getLogger(__name__)


@enum.unique  # pylint: disable=W0232
class Events(enum.Enum):
    shaker_input_needed = 1000
    mover_input_needed = 1001
    giver_input_needed = 1002

    hand_complete = 2000


def event_notify(game_id, player_id, event_type):
    """ Notification stub """
    logger.debug("Notification for Game %s, Player %s, Event %s",
                 game_id, player_id, event_type)
