import pytest

from lohai.game.deck import Card, CardValue, Deck, Suit, SpecialCard
from lohai.game.round import Hand, Round


@pytest.fixture
def clean_deck():
    return Deck.shuffle_new_deck()


@pytest.fixture(scope="session",
                params=[CardValue.taker,
                        CardValue.giver,
                        CardValue.mover,
                        CardValue.shaker])
def special_card(request):
    return SpecialCard(request.param)


@pytest.fixture()
def first_player():
    return 0


@pytest.fixture()
def hand(round, first_player):  # pylint: disable=W0621
    return Hand(round, first_player)


# the default hands, trump_card and deck were generated via start_new_round,
# the hands have been sorted for easier reading
@pytest.fixture()
def hands():
    return [[Card(CardValue.three, Suit.spade),
             Card(CardValue.seven, Suit.spade),
             Card(CardValue.king, Suit.spade),
             Card(CardValue.eight, Suit.heart),
             Card(CardValue.eight, Suit.club),
             Card(CardValue.queen, Suit.club),
             Card(CardValue.eight, Suit.diamond),
             Card(CardValue.jack, Suit.diamond),
             SpecialCard(CardValue.taker)],

            [Card(CardValue.four, Suit.spade),
             Card(CardValue.six, Suit.spade),
             Card(CardValue.nine, Suit.spade),
             Card(CardValue.five, Suit.heart),
             Card(CardValue.nine, Suit.heart),
             Card(CardValue.king, Suit.club),
             Card(CardValue.three, Suit.diamond),
             Card(CardValue.four, Suit.diamond),
             SpecialCard(CardValue.shaker)],

            [Card(CardValue.five, Suit.spade),
             Card(CardValue.eight, Suit.spade),
             Card(CardValue.queen, Suit.spade),
             Card(CardValue.two, Suit.heart),
             Card(CardValue.six, Suit.club),
             Card(CardValue.nine, Suit.club),
             Card(CardValue.two, Suit.diamond),
             Card(CardValue.six, Suit.diamond),
             Card(CardValue.seven, Suit.diamond)],

            [Card(CardValue.four, Suit.heart),
             Card(CardValue.seven, Suit.heart),
             Card(CardValue.queen, Suit.heart),
             Card(CardValue.two, Suit.club),
             Card(CardValue.five, Suit.club),
             Card(CardValue.seven, Suit.club),
             SpecialCard(CardValue.taker),
             SpecialCard(CardValue.mover),
             SpecialCard(CardValue.giver)]]


@pytest.fixture()
def trump_card():
    return Card(CardValue.king, Suit.heart)  # heart king


@pytest.fixture()
def deck():
    return Deck([Card(CardValue.jack, Suit.club),
                 Card(CardValue.queen, Suit.diamond),
                 Card(CardValue.jack, Suit.spade),
                 Card(CardValue.jack, Suit.heart),
                 SpecialCard(CardValue.shaker),
                 Card(CardValue.three, Suit.club),
                 Card(CardValue.three, Suit.heart),
                 SpecialCard(CardValue.mover),
                 Card(CardValue.two, Suit.spade),
                 Card(CardValue.five, Suit.diamond),
                 Card(CardValue.six, Suit.heart),
                 Card(CardValue.king, Suit.diamond),
                 SpecialCard(CardValue.giver),
                 Card(CardValue.four, Suit.club),
                 Card(CardValue.nine, Suit.diamond)])


@pytest.fixture()
def round(deck, hands, trump_card):  # pylint: disable=W0621
    return Round(deck, hands, trump_card)
