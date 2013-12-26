# pylint: disable=R0201

import pytest

from lohai import exception
from lohai.game.deck import Card, CardValue, Deck, SpecialCard, Suit
from lohai.game.round import Round


class TestCanPlayCards(object):
    """ Tests around whether or not players are allowed to play a card """
    # these tests are easier with a simpler set of hands
    @pytest.fixture()
    def hands(self):
        hands = [[Card(CardValue.two, Suit.club),
                  SpecialCard(CardValue.taker)],

                 [Card(CardValue.three, Suit.club),
                  SpecialCard(CardValue.taker),
                  Card(CardValue.four, Suit.heart)],

                 [Card(CardValue.four, Suit.diamond),
                  Card(CardValue.two, Suit.spade)],

                 [Card(CardValue.five, Suit.club),
                  Card(CardValue.six, Suit.diamond)]]

        return hands

    def test_cannot_play_cards_not_in_hand(self, hands, round):
        # first player tries to play player 2's card
        with pytest.raises(exception.InvalidCard):
            round.play_card(0, hands[1][0])

        # first player pulls a card out of his sleeve
        with pytest.raises(exception.InvalidCard):
            round.play_card(0, Card(CardValue.taker, Suit.club))

    def test_play_in_order(self, hands, round):
        """ Players play clockwise one at a time """
        # first player plays a card
        round.play_card(0, hands[0][0])

        # third player tries to go out of turn
        with pytest.raises(exception.NotYourTurn):
            round.play_card(2, hands[2][0])

        # each player carries on in turn
        round.play_card(1, hands[1][0])
        round.play_card(2, hands[2][0])
        round.play_card(3, hands[3][0])

    def test_suit_follow(self, hands, round):
        """ Ensure players follow suit if able """
        # first player plays a club
        round.play_card(0, hands[0][0])

        # second player must also play a club because he has one
        with pytest.raises(exception.InvalidCard):
            round.play_card(1, hands[1][2])
        round.play_card(1, hands[1][0])

        # third player does not have a club and may play any card
        round.play_card(2, hands[2][0])

        # fourth play must play a club because he has one
        with pytest.raises(exception.InvalidCard):
            round.play_card(3, hands[3][1])
        round.play_card(3, hands[3][0])

    def test_special_instead_of_suit(self, hands, round):
        """ Ensure players can always play a special card """
        # first player plays a club
        round.play_card(0, hands[0][0])

        # second player plays a taker, even though he has a club
        round.play_card(1, hands[1][1])

    def test_second_player_determines_suit(self, hands, round):
        """ First suited card played determines the suit """
        # first player plays a taker
        round.play_card(0, hands[0][0])

        # second player plays a club, setting the suit
        round.play_card(1, hands[1][0])

        # third player plays whatever becuase he doesn't have a club
        round.play_card(2, hands[2][0])

        # fourth player must play his club
        with pytest.raises(exception.InvalidCard):
            round.play_card(3, hands[3][1])

        round.play_card(3, hands[3][0])


class TestRound(object):
    def test_round_start(self):
        """ Ensure round start conditions valid

        at the start of the round each player has 9 cards and the round has a
        trump suit and a point value
        """
        r = Round.start_new_round()
        assert isinstance(r.pointvalue, int)
        assert r.trump_suit in Suit
        for player in range(r.player_count):
            assert 9 == len(r.get_hand_for_player(player))


class TestTricks(object):
    """ Tests around various trick win conditions """
    def test_highest_lead_suit_wins(self, round):
        """ the player with the highest lead suit card wins """
        round.play_card(0, Card(CardValue.three, Suit.spade))
        round.play_card(1, Card(CardValue.four, Suit.spade))
        # highest lead suit in the play
        round.play_card(2, Card(CardValue.five, Suit.spade))
        # higher, but not a spade
        round.play_card(3, Card(CardValue.seven, Suit.club))

        # player 3 should have a point
        assert [0, 0, 1, 0] == round.tricks_won

    def test_last_taker_wins(self, round):
        """ Last taker played wins, and the player of the taker leads the next
        trick """
        round.play_card(0, SpecialCard(CardValue.taker))
        round.play_card(1, Card(CardValue.four, Suit.spade))
        round.play_card(2, Card(CardValue.five, Suit.spade))
        round.play_card(3, SpecialCard(CardValue.taker))

        # player 4 should have a point
        assert [0, 0, 0, 1] == round.tricks_won

        # the winner of the previous trick leads the next
        # player 1 is not allowed to go next
        with pytest.raises(exception.NotYourTurn):
            round.play_card(0, Card(CardValue.three, Suit.spade))

        # player 4 gets to go first next trick
        round.play_card(3, Card(CardValue.four, Suit.heart))

    def test_last_giver_wins(self, round):
        """ Last giver played wins, may give the trick to anyone other than
        himself.  The recipient of the trick leads the next trick
        """
        round.play_card(0, SpecialCard(CardValue.taker))
        round.play_card(1, Card(CardValue.four, Suit.spade))
        round.play_card(2, Card(CardValue.five, Suit.spade))
        round.play_card(3, SpecialCard(CardValue.giver))

        with pytest.raises(exception.InvalidMove):
            # last player cannot give the trick to himself
            round.handle_giver(3)

        # last player gives it to player 2
        round.handle_giver(1)

        # player 2 should have a point
        assert [0, 1, 0, 0] == round.tricks_won

        # last player doesn't get to go, player 2 does
        with pytest.raises(exception.NotYourTurn):
            round.play_card(3, Card(CardValue.four, Suit.heart))

        round.play_card(1, Card(CardValue.six, Suit.spade))

    def test_highest_trump_suit_wins(self, round, trump_card):
        """ Highest trump suit wins regardless of lead suit """
        # precondition
        assert trump_card.suit == Suit.heart

        round.play_card(0, Card(CardValue.seven, Suit.spade))
        round.play_card(1, Card(CardValue.four, Suit.spade))
        round.play_card(2, Card(CardValue.five, Suit.spade))
        # last player trumps
        round.play_card(3, Card(CardValue.four, Suit.heart))

        # player 4 should have a point
        assert [0, 0, 0, 1] == round.tricks_won


class TestShaker(object):
    """ Tests around shaker behavior """
    @pytest.fixture()
    def hands(self):
        return [[Card(CardValue.three, Suit.heart)],
                [Card(CardValue.four, Suit.heart)],
                [SpecialCard(CardValue.shaker)],
                [Card(CardValue.five, Suit.heart)]]

    @pytest.fixture()
    def deck(self):
        return Deck([SpecialCard(CardValue.shaker),
                     Card(CardValue.five, Suit.heart)])

    def test_shaker_steal_card(self, hands, round):
        """ a player who plays a shaker can steal another players card, and the
        victim draws a card """

        expected_field = [Card(CardValue.three, Suit.heart),
                          SpecialCard(CardValue.shaker),
                          Card(CardValue.four, Suit.heart),
                          None]

        # player 1 plays a card
        round.play_card(0, hands[0][0])
        # so does player 2
        round.play_card(1, hands[1][0])

        # player 3 plays a shaker
        round.play_card(2, hands[2][0])

        # can't steal player 4's card
        with pytest.raises(exception.InvalidMove):
            round.handle_shaker(2, 3)

        # player 2 doesn't get to steal anybody's anything
        with pytest.raises(exception.InvalidMove):
            round.handle_shaker(1, 0)

        round.handle_shaker(2, 1)

        assert expected_field == round.this_rounds_cards

    def test_shaker_first(self, round, hands):
        """ a player who plyas a shaker first simply draws a new card from the
        top of the deck """
        expected_field = [None, None, Card(CardValue.five, Suit.heart),
                          None]

        round.cur_player = round.first_player = 2

        # play a shaker first, draw a card
        round.play_card(2, hands[2][0])

        assert expected_field == round.this_rounds_cards

    def test_shaker_back(self, round, hands):
        """ Shaker back and forth test

        a player who plays a shaker can steal another players card, and the
        victim draws a card.  If the card is a shaker they can steal their card
        back
        """
        expected_field = [None, Card(CardValue.four, Suit.heart),
                          Card(CardValue.five, Suit.heart), None]
        round.cur_player = round.first_player = 1

        # play a card
        round.play_card(1, hands[1][0])

        # shake it
        round.play_card(2, hands[2][0])
        round.handle_shaker(2, 1)

        # shake it back
        round.handle_shaker(1, 2)

        assert expected_field == round.this_rounds_cards


class TestMover(object):
    @pytest.fixture(params=[[0, 0, 0, 1],  # high count
                            [1, 1, 1, 0],  # low count
                            [1, 1, 2, 2],  # tied count
                            ])
    def tricks_won(self, request):
        return request.param

    def test_mover_with_invalid_counts(self, tricks_won, round):
        """ A player who plays a mover when he is not definitively in the
        middle draws a card from the deck
        """
        round.cur_player = 3
        round.tricks_won = tricks_won

        expected_field = [None, None, None, Card(CardValue.jack, Suit.club)]

        # player 4 plays a mover
        round.play_card(3, SpecialCard(CardValue.mover))

        # player 4 is winning, so they aren't allowed to move
        with pytest.raises(exception.InvalidMove):
            round.handle_mover(3, 3, 1)

        assert expected_field == round.this_rounds_cards

    def test_mover_source_player_empty(self, round):
        round.cur_player = 3
        round.tricks_won = [0, 2, 2, 1]

        # player 4 plays a mover
        round.play_card(3, SpecialCard(CardValue.mover))

        # player 4 may not move a trick from player 1 (he doesn't have one!)
        with pytest.raises(exception.InvalidMove):
            round.handle_mover(3, 0, 1)

        # player 4 moves a trick from himself to player 1
        round.handle_mover(3, 3, 0)

        expected_field = [None, None, None,
                          Card(CardValue.jack, Suit.club)]
        expected_tricks = [1, 2, 2, 0]

        assert expected_tricks == round.tricks_won
        assert expected_field == round.this_rounds_cards
