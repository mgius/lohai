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


class CardTests(unittest.TestCase):
    def test_card_ordering(self):
        shaker = Card(CardValue.shaker, Suit.heart)
        two_club = Card(2, Suit.club)
        three_club = Card(3, Suit.club)
        three_diamonds = Card(3, Suit.diamond)
        four_hearts = Card(4, Suit.heart)
        five_spade = Card(5, Suit.spade)

        order = [five_spade, four_hearts, two_club, three_club, three_diamonds,
                 shaker]

        for i in range(0, len(order)):
            for j in range(i + 1, len(order)):
                self.assertLess(order[i], order[j])
                self.assertGreater(order[j], order[i])


class DeckTests(unittest.TestCase):
    def test_correct_card_count(self):
        """ There should be 52 cards """
        self.assertEqual(52, len(Deck.shuffle_new_deck().cards))


class RoundTests(unittest.TestCase):
    def test_round_start(self):
        """ Ensure round start conditions valid

        at the start of the round each player has 9 cards and the round has a
        trump suit and a point value
        """
        r = Round.start_new_round()
        self.assertTrue(isinstance(r.pointvalue, int))
        self.assertIn(r.trump_suit, Suit.all_suits + [Suit.none])
        for player in range(r.player_count):
            self.assertEqual(9, len(r.get_hand_for_player(player)))


class CanPlayCardsTests(unittest.TestCase):
    """ Tests around whether or not players are allowed to play a card """
    def test_cannot_play_cards_not_in_hand(self):
        hands = [[Card(2, Suit.club), Card(2, Suit.diamond)],
                 [Card(3, Suit.club), Card(2, Suit.heart)],
                 [Card(4, Suit.diamond), Card(2, Suit.spade)],
                 [Card(5, Suit.club), Card(6, Suit.diamond)]]

        r = Round(None, hands, None, None)

        # first player tries to play player 2's card
        with self.assertRaises(exception.InvalidCard):
            r.play_card(0, hands[1][0])

        # first player pulls a card out of his sleeve
        with self.assertRaises(exception.InvalidCard):
            r.play_card(0, Card(CardValue.taker, Suit.club))

    def test_play_in_order(self):
        """ Players play clockwise one at a time """
        hands = [[Card(2, Suit.club), Card(2, Suit.diamond)],
                 [Card(3, Suit.club), Card(2, Suit.heart)],
                 [Card(4, Suit.diamond), Card(2, Suit.spade)],
                 [Card(5, Suit.club), Card(6, Suit.diamond)]]
        r = Round(None, hands, None, None)

        # first player plays a card
        r.play_card(0, hands[0][0])

        # third player tries to go out of turn
        with self.assertRaises(exception.NotYourTurn):
            r.play_card(2, hands[2][0])

        # each player carries on in turn
        r.play_card(1, hands[1][0])
        r.play_card(2, hands[2][0])
        r.play_card(3, hands[3][0])

    def test_suit_follow(self):
        """ Ensure players follow suit if able """
        hands = [[Card(2, Suit.club), Card(2, Suit.diamond)],
                 [Card(3, Suit.club), Card(2, Suit.heart)],
                 [Card(4, Suit.diamond), Card(2, Suit.spade)],
                 [Card(5, Suit.club), Card(6, Suit.diamond)]]

        round = Round(None, hands, None, None)

        # first player plays a club
        round.play_card(0, hands[0][0])

        # second player must also play a club because he has one
        with self.assertRaises(exception.InvalidCard):
            round.play_card(1, hands[1][1])
        round.play_card(1, hands[1][0])

        # third player does not have a club and may play any card
        round.play_card(2, hands[2][0])

        # fourth play must play a club because he has one
        with self.assertRaises(exception.InvalidCard):
            round.play_card(3, hands[3][1])
        round.play_card(3, hands[3][0])

    def test_special_instead_of_suit(self):
        """ Ensure players can always play a special card """
        hands = [[Card(2, Suit.club), Card(2, Suit.diamond)],
                 [Card(3, Suit.club), Card(CardValue.taker, Suit.spade)],
                 [Card(4, Suit.diamond), Card(2, Suit.spade)],
                 [Card(5, Suit.club), Card(6, Suit.diamond)]]

        round = Round(None, hands, None, None)

        # first player plays a club
        round.play_card(0, hands[0][0])

        # second player plays a taker, even though he has a club
        round.play_card(1, hands[1][1])

    def test_second_player_determines_suit(self):
        """ First suited card played determines the suit """
        hands = [[Card(CardValue.taker, Suit.club), Card(2, Suit.diamond)],
                 [Card(3, Suit.club), Card(2, Suit.heart)],
                 [Card(4, Suit.diamond), Card(2, Suit.spade)],
                 [Card(5, Suit.club), Card(6, Suit.diamond)]]

        round = Round(None, hands, None, None)

        # first player plays a taker
        round.play_card(0, hands[0][0])

        # second player plays a club, setting the suit
        round.play_card(1, hands[1][0])

        # third player plays whatever becuase he doesn't have a club
        round.play_card(2, hands[2][0])

        # fourth player must play his club
        with self.assertRaises(exception.InvalidCard):
            round.play_card(3, hands[3][1])

        round.play_card(3, hands[3][0])


class LohaiTests(unittest.TestCase):
    def setUp(self):
        # this set of hands generated using the Round.start_new_round and then
        # sorted
        self.hands = [[Card(3, 0), Card(7, 0), Card(12, 0), Card(8, 1),
                       Card(8, 2), Card(11, 2), Card(8, 3), Card(10, 3),
                       Card(13, 0)],
                      [Card(4, 0), Card(6, 0), Card(9, 0), Card(5, 1),
                       Card(9, 1), Card(12, 2), Card(3, 3), Card(4, 3),
                       Card(14, 3)],
                      [Card(5, 0), Card(8, 0), Card(11, 0), Card(2, 1),
                       Card(6, 2), Card(9, 2), Card(2, 3), Card(6, 3),
                       Card(7, 3)],
                      [Card(4, 1), Card(7, 1), Card(11, 1), Card(2, 2),
                       Card(5, 2), Card(7, 2), Card(13, 2), Card(13, 3),
                       Card(14, 2)]]

        self.deck = Deck([Card(10, 2), Card(11, 3), Card(10, 0), Card(10, 1),
                          Card(14, 1), Card(3, 2), Card(3, 1),
                          Card(13, 1), Card(2, 0), Card(5, 3), Card(6, 1),
                          Card(12, 3), Card(14, 0), Card(4, 2), Card(9, 3)])

        self.trump_card = Card(12, 1)  # heart king

        self.round = Round(self.deck, self.hands, self.trump_card.pointvalue,
                           self.trump_card.suit)


class TrickTests(LohaiTests):
    """ Tests around various trick win conditions """
    def test_highest_lead_suit_wins(self):
        """ the player with the highest lead suit card wins """
        # player 1 plays a middle club
        self.round.play_card(0, Card(3, 0))

        # player 2 plays a lower club
        self.round.play_card(1, Card(4, 0))

        # player 3 plays another lower club
        self.round.play_card(2, Card(5, 0))

        # player 4 plays a high non-club
        self.round.play_card(3, Card(7, 2))

        # player 3 should have a point
        self.assertEqual([0, 0, 1, 0], self.round.tricks_won)

    def test_last_taker_wins(self):
        """ Last taker played wins, and the player of the taker leads the next
        trick """
        # first player plays a taker
        self.round.play_card(0, Card(13, 0))

        # second player sets the suit as club
        self.round.play_card(1, Card(4, 0))

        # third player follows with a club
        self.round.play_card(2, Card(5, 0))

        # last player plays a taker
        self.round.play_card(3, Card(13, 2))

        # player 4 should have a point
        self.assertEqual([0, 0, 0, 1], self.round.tricks_won)

        # player 1 is not allowed to go next
        with self.assertRaises(exception.NotYourTurn):
            self.round.play_card(0, Card(3, 0))

        # player 4 gets to go first next trick
        self.round.play_card(3, Card(4, 1))

        # the winner of the previous trick leads the next

    def test_last_giver_wins(self):
        """ Last giver played wins, may give the trick to anyone other than
        himself.  The recipient of the trick leads the next trick
        """
        # first player plays a taker
        self.round.play_card(0, Card(13, 0))

        # second player sets the suit as club
        self.round.play_card(1, Card(4, 0))

        # third player follows with a club
        self.round.play_card(2, Card(5, 0))

        # last player plays a taker
        self.round.play_card(3, Card(14, 2))

        with self.assertRaises(exception.InvalidMove):
            # last player cannot give the trick to himself
            self.round.handle_giver(3)

        # last player gives it to player 2
        self.round.handle_giver(1)

        # player 2 should have a point
        self.assertEqual([0, 1, 0, 0], self.round.tricks_won)

        # last player doesn't get to go, player 2 does
        with self.assertRaises(exception.NotYourTurn):
            self.round.play_card(3, Card(4, 1))

        self.round.play_card(1, Card(6, 0))

    def test_highest_trump_suit_wins(self):
        """ Highest trump suit wins regardless of lead suit """
        # player 1 leads a middle club
        self.round.play_card(0, Card(7, 0))

        # player 2 plays a lower club
        self.round.play_card(1, Card(4, 0))

        # player 3 plays another lower club
        self.round.play_card(2, Card(5, 0))

        # last player trumps
        self.round.play_card(3, Card(4, 1))

        # player 4 should have a point
        self.assertEqual([0, 0, 0, 1], self.round.tricks_won)


class ShakerTests(unittest.TestCase):
    """ Tests around shaker behavior """
    def test_shaker_steal_card(self):
        """ a player who plays a shaker can steal another players card, and the
        victim draws a card """
        hands = [[Card(3,1)],
                 [Card(4,1)],
                 [Card(CardValue.shaker, Suit.heart)],
                 []]

        deck = Deck([Card(5,1)])

        expected_field = [Card(3, 1), Card(5, 1), Card(4, 1), None]

        trump_card = Card(12, 1)

        round = Round(deck, hands, trump_card.pointvalue, trump_card.suit)

        # player 1 plays a card
        round.play_card(0, hands[0][0])
        # so does player 2
        round.play_card(1, hands[1][0])

        # player 3 plays a shaker
        round.play_card(2, hands[2][0])

        # can't steal player 4's card 
        with self.assertRaises(exception.InvalidMove):
            round.handle_shaker(2, 3)

        # player 2 doesn't get to steal anybody's anything
        with self.assertRaises(exception.InvalidMove):
            round.handle_shaker(1, 0)

        round.handle_shaker(2, 1)

        self.assertEqual(expected_field, round.this_rounds_cards)

    def test_shaker_first(self):
        """ a player who plyas a shaker first simply draws a new card from the
        top of the deck """
        hands = [[Card(CardValue.shaker, Suit.heart)],
                 [],
                 [],
                 []]

        deck = Deck([Card(5,1)])

        expected_field = [Card(5, 1), None, None, None]

        trump_card = Card(12, 1)

        round = Round(deck, hands, trump_card.pointvalue, trump_card.suit)

        # play a shaker first, draw a card
        round.play_card(0, hands[0][0])

        self.assertEqual(expected_field, round.this_rounds_cards)


    def test_shaker_back(self):
        hands = [[Card(3,1)],
                 [Card(CardValue.shaker, Suit.heart)],
                 [],
                 []]

        deck = Deck(
            [Card(CardValue.shaker, Suit.diamond),
             Card(4, 1)])

        expected_field = [Card(3, 1), Card(4, 1), None, None]
        trump_card = Card(12, 1)

        round = Round(deck, hands, trump_card.pointvalue, trump_card.suit)

        # play a card
        round.play_card(0, hands[0][0])

        # shake it
        round.play_card(1, hands[1][0])
        round.handle_shaker(1, 0)

        # shake it back
        round.handle_shaker(0, 1)

        self.assertEqual(expected_field, round.this_rounds_cards)



# a player who plays a shaker can steal another players card, and the victim
# draws a card.  If the card is a shaker they can steal their call back

# A player who plays a mover who has the high or low count (or is tied for
# either) simply draws a new card from the deck

# A player who plays a mover who does not have the high or low count allows the
# player to immediately move a previously won trick from any player to any
# other.  Afterwards they draw a new card from the top of the deck.


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
