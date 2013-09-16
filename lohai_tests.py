import unittest

from lohai import exception
from lohai.deck import Card, CardValue, Deck, Suit
from lohai.round import Round


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
        hands = [[Card(2, Suit.club), Card(2, Suit.diamond)],
                 [Card(3, Suit.club), Card(CardValue.taker, Suit.spade)],
                 [Card(4, Suit.diamond), Card(2, Suit.spade)],
                 [Card(5, Suit.club), Card(6, Suit.diamond)]]

        round = Round(None, hands, None, None)

        # first player plays a club
        round.play_card(0, hands[0][0])

        # second player plays a taker, even though he has a club
        round.play_card(1, hands[1][1])



# players may play a special card even if they can follow suit

# the first player to play a suited card determines the suit, subsequent
# players follow suit as before

# the last player to play a giver or taker (black special) wins

# the player with the highest trump suit wins, regardless of lead suit

# the player with the highest number in the lead suit wins

# the winner of the previous trick leads the next

# the player who plays the giver may give the trick to any player other than
# himself

# the recipient of a giver trick leads the next trick

# the player who plays the taker receives the trick

# A player who plays a mover who has the high or low count (or is tied for
# either) simply draws a new card from the deck

# A player who plays a mover who does not have the high or low count allows the
# player to immediately move a previously won trick from any player to any
# other.  Afterwards they draw a new card from the top of the deck.

# a player who plays a shaker can steal another players card, and the victim
# draws a card

# a player who plyas a shaker first simply draws a new card from the top of the
# deck

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

# a player who plays a shaker can steal another players card, and the victim
# draws a card.  If the card is a shaker they can steal their call back

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
