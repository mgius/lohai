import pytest

from lohai.game.deck import Card, CardValue, SpecialCard, Suit


def test_special_card_is_special(special_card):
    assert special_card.is_special


def test_card_ordering():
    shaker = SpecialCard(CardValue.shaker)
    two_club = Card(CardValue.two, Suit.club)
    three_club = Card(CardValue.three, Suit.club)
    three_diamonds = Card(CardValue.three, Suit.diamond)
    four_hearts = Card(CardValue.four, Suit.heart)
    five_spade = Card(CardValue.five, Suit.spade)

    order = [five_spade, four_hearts, two_club, three_club, three_diamonds,
             shaker]

    for i in range(0, len(order)):
        for j in range(i + 1, len(order)):
            assert order[i] < order[j]
            assert order[j] > order[i]


def test_correct_card_count(clean_deck):
    """ There should be 52 cards """
    assert 52 == len(clean_deck.cards)


def test_can_pop_all_cards(clean_deck):
    """ Should be able to draw 52 cards from the deck """
    for _i in range(52):
        clean_deck.draw_card()

    with pytest.raises(IndexError):
        clean_deck.draw_card()


def test_card_constructor():
    with pytest.raises(Exception):
        Card(CardValue.two, Suit.club.value)

    with pytest.raises(Exception):
        Card(CardValue.two.value, Suit.club)

    with pytest.raises(Exception):
        SpecialCard(CardValue.two)

    with pytest.raises(Exception):
        SpecialCard(CardValue.shaker, suit=Suit.club)


def test_coverage_str_repr(special_card):
    # clear coverage for __str__ and __repr__ debugging helpers
    repr(special_card)
    str(special_card)
