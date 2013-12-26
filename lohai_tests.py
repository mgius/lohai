import unittest

from lohai import exception
from lohai.deck import Card, CardValue, Deck, Suit
from lohai.events import Event
from lohai.round import Round


class TestEvent1(Event):
    pass


class TestEvent2(Event):
    pass


class EventTests(unittest.TestCase):
    def setUp(self):
        self.TestEvent1 = Event('TestEvent1')
        self.TestEvent2 = Event('TestEvent2')

    def test_event_notify(self):
        self.counter1 = 0
        self.counter2 = 0

        def inc_counter1():
            self.counter1 += 1

        def inc_counter2():
            self.counter2 += 1

        self.TestEvent1.register(inc_counter1)
        self.TestEvent2.register(inc_counter2)

        self.assertEqual(0, self.counter1)
        self.assertEqual(0, self.counter2)

        self.TestEvent1.notify()

        self.assertEqual(1, self.counter1)
        self.assertEqual(0, self.counter2)

        self.TestEvent2.notify()

        self.assertEqual(1, self.counter1)
        self.assertEqual(1, self.counter2)

        del inc_counter1, inc_counter2

        self.TestEvent1.notify()
        self.TestEvent2.notify()

        self.assertEqual(1, self.counter1)
        self.assertEqual(1, self.counter2)

        self.assertEqual(0, len(self.TestEvent1.callbacks))
        self.assertEqual(0, len(self.TestEvent2.callbacks))


# At the end of the hand, the two players that have the least tricks (the Lo)
# and most tricks (the Hai) score points. If two or more players tie for either
# Lo or Hai, no players score those points.

# The person who reaches 1,500 points first wins the game. If two players reach
# 1,500 points in the same deal, the side with the higher score wins. If the
# two players are tied, both players win.

# If you play a red special card as the lead, the random card from the stack
# you put on top of it to replace it is the lead suit.

# If a black special card is played first, the next player is free to play
# whatever he would like. If he chooses to play a suited card, that is
# considered the lead suit.


# if a player draws a giver or taker as a result of a shaker they trump
# previously played givers and takers


# FUTURE
# Three Player Lohai Instead of going for Hai or Lo, the objective is to be the
# player who is either the middle trick taker or the one who did not tie the
# other two players. Typically, this means each hand will have two players with
# three tricks and the scoring player with four tricks.
#
# All rules are the same except 10 cards are dealt instead of 9 and the Mover
# only works if you are either Lo or Hai. If you are tied for either Lo or Hai,
# the Mover does not work.
