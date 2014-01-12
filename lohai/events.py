import enum
import logging
import weakref


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


class Event(object):
    def __init__(self, event_name):
        self.event_name = event_name
        self.callbacks = []

    def register(self, callback):
        self.callbacks.append(weakref.ref(callback))

    def unregister(self, to_remove):
        for cb_ref in self.callbacks[:]:
            callback = cb_ref()
            if callback is not None and callback == to_remove:
                self.callbacks.remove(cb_ref)
                break

    def notify(self, *args, **kwargs):
        for cb_ref in self.callbacks[:]:
            # dereference weakref
            callback = cb_ref()
            if callback is None:
                # remove any callbacks which have been gc'd
                self.callbacks.remove(cb_ref)
            else:
                callback(*args, **kwargs)

    def clear(self):
        self.callbacks = []
