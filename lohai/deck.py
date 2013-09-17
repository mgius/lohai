from functools import total_ordering
from itertools import product, starmap
import random


class Suit(object):
    none = -1
    spade = 0
    heart = 1
    club = 2
    diamond = 3

    all_suits = [spade, heart, club, diamond]
    black_suits = [spade, club]
    red_suits = [heart, diamond]


class CardValue(object):
    jack = 11
    queen = 12
    king = 13
    taker = 14   # black
    giver = 15   # black
    mover = 14   # red
    shaker = 15  # red

    all_values = range(2, 16)
    special_values = [14, 15]


@total_ordering
class Card(object):
    __slots__ = ['_value', '_suit']

    def __init__(self, value, suit):
        if value not in CardValue.all_values:
            raise Exception("%s is not a valid cardvalue" % value)
        if suit not in Suit.all_suits:
            raise Exception("%s is not a valid suit value" % suit)

        self._value = value
        self._suit = suit

    def __eq__(self, other):
        return self.value == other.value and self.suit == other.suit

    def __lt__(self, other):
        # order special cards last, then order by suit and value
        self_special = self.is_special()
        other_special = other.is_special()

        if self_special and not other_special:
            return False

        if not self_special and other_special:
            return True

        if self.suit == other.suit:
            return self.value < other.value
        else:
            return self.suit < other.suit

    def __getstate__(self):
        return {'_value': self._value,
                '_suit': self._suit}

    def __setstate__(self, state):
        self._value = state['_value']
        self._suit = state['_suit']

    @property
    def pointvalue(self):
        if self.is_special():
            if self.is_taker():
                return 425
            elif self.is_mover():
                return 450
            elif self.is_giver():
                return 125
            elif self.is_shaker():
                return 100
        else:
            return 100 + self.value * 25

    @property
    def value(self):
        return self._value

    @property
    def suit(self):
        return self._suit

    def is_special(self):
        return self.value in CardValue.special_values

    def is_taker(self):
        return self.value == CardValue.taker and self.suit in Suit.black_suits

    def is_mover(self):
        return self.value == CardValue.mover and self.suit in Suit.red_suits

    def is_giver(self):
        return self.value == CardValue.giver and self.suit in Suit.black_suits

    def is_shaker(self):
        return self.value == CardValue.shaker and self.suit in Suit.red_suits

    def _special_to_str(self):
        if self.is_taker():
            return 'Taker'
        elif self.is_mover():
            return 'Mover'
        elif self.is_giver():
            return 'Giver'
        elif self.is_shaker():
            return 'Shaker'

    def _normal_to_str(self):
        suit_str = {Suit.spade: 'Spades',
                    Suit.heart: 'Hearts',
                    Suit.club: 'Clubs',
                    Suit.diamond: 'Diamonds'}.get(self.suit)
        value_str = {CardValue.jack: 'Jack',
                     CardValue.queen: 'Queen',
                     CardValue.king: 'King'}.get(self.value, self.value)

        return "%s of %s" % (value_str, suit_str)

    def __str__(self):
        if self.is_special():
            return self._special_to_str()
        else:
            return self._normal_to_str()

    def __repr__(self):
        return 'Card(%s, %s)' % (self.value, self.suit)


class Deck(object):
    def __init__(self, cards):
        self.cards = cards

    @staticmethod
    def shuffle_new_deck():
        cards = list(starmap(Card, product(CardValue.all_values,
                                           Suit.all_suits)))
        random.shuffle(cards)
        return Deck(cards)

    def draw_card(self):
        return self.cards.pop()
