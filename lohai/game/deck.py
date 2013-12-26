import enum
from functools import total_ordering
from itertools import product, starmap
import random


@enum.unique  # pylint: disable=W0232
class Suit(enum.IntEnum):
    spade = 0
    heart = 1
    club = 2
    diamond = 3
    none = 4

    @classmethod
    def black_suits(cls):
        return [cls.spade, cls.club]

    @classmethod
    def red_suits(cls):
        return [cls.heart, cls.diamond]

    @classmethod
    def all_suits(cls):
        return cls.red_suits() + cls.black_suits()


@enum.unique  # pylint: disable=W0232
class CardValue(enum.IntEnum):
    shaker = 0
    giver = 1
    two = 2
    three = 3
    four = 4
    five = 5
    six = 6
    seven = 7
    eight = 8
    nine = 9
    jack = 10
    queen = 11
    king = 12
    taker = 13
    mover = 14

    @classmethod
    def number_values(cls):
        return [cls.two, cls.three, cls.four, cls.five, cls.six, cls.seven,
                cls.eight, cls.nine, cls.jack, cls.queen, cls.king]

    @classmethod
    def special_values(cls):
        return [cls.taker, cls.giver, cls.mover, cls.shaker]


@total_ordering
class Card(object):
    is_special = False

    def __init__(self, value, suit):
        if value not in CardValue:
            raise Exception("%s is not a valid cardvalue" % value)
        if suit not in Suit:
            raise Exception("%s is not a valid suit value" % suit)

        self._value = value
        self._suit = suit

    def __eq__(self, other):
        if other is None:
            return False
        return self.value == other.value and self.suit == other.suit

    def __lt__(self, other):
        # order special cards last, then order by suit and value
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
        return 100 + self.value * 25

    @property
    def value(self):
        return self._value

    @property
    def suit(self):
        return self._suit

    # these are kind of lame...
    def is_mover(self):
        return self.value == CardValue.mover

    def is_shaker(self):
        return self.value == CardValue.shaker

    def is_giver(self):
        return self.value == CardValue.giver

    def is_taker(self):
        return self.value == CardValue.taker

    def __str__(self):
        suit_str = {Suit.spade: 'Spades',
                    Suit.heart: 'Hearts',
                    Suit.club: 'Clubs',
                    Suit.diamond: 'Diamonds'}.get(self.suit)
        value_str = {CardValue.jack: 'Jack',
                     CardValue.queen: 'Queen',
                     CardValue.king: 'King'}.get(self.value, self.value)

        return "%s of %s" % (value_str, suit_str)

    def __repr__(self):
        return 'Card(%s, %s)' % (self.value.name, self.suit.name)


class SpecialCard(Card):
    __slots__ = ['_value', '_suit']
    is_special = True

    def __init__(self, value, suit=Suit.none):
        if suit != Suit.none:
            raise Exception("Special cards have no suit")

        super(SpecialCard, self).__init__(value, suit)

    def __str__(self):
        return {CardValue.taker: 'Taker',
                CardValue.mover: 'Mover',
                CardValue.giver: 'Giver',
                CardValue.shaker: 'Shaker'}[self.value]


class Deck(object):
    def __init__(self, cards):
        self.cards = cards

    @staticmethod
    def shuffle_new_deck():
        cards = list(starmap(Card, product(CardValue.number_values(),
                                           Suit.all_suits())))

        for special_value in CardValue.special_values():
            # two of each kind of special card
            cards.append(SpecialCard(special_value))
            cards.append(SpecialCard(special_value))

        random.shuffle(cards)
        return Deck(cards)

    def draw_card(self):
        return self.cards.pop(0)
