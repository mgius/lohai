import copy
import lohai.deck


class Round(object):
    def __init__(self, deck, hands, pointvalue, trump_suit):
        self.deck = deck
        self.hands = hands
        self.pointvalue = pointvalue
        self.trump_suit = trump_suit

    @staticmethod
    def start_new_round():
        deck = lohai.deck.Deck.shuffle_new_deck()

        hands = [list(), list(), list(), list()]

        handsize = 9
        for i in range(handsize):
            for hand in hands:
                hand.append(deck.draw_card())

        trump_card = deck.draw_card().pointvalue
        if trump_card.is_special():
            # if a special card is turned, there is no trump for the hand
            trump_suit = lohai.deck.Suit.none
        else:
            trump_suit = trump_card.suit

        return Round(deck, hands, trump_card.pointvalue, trump_suit)

    def get_hand_for_player(self, player):
        return copy.deepcopy(self.hands[player])

    def play_card(self, player, card):
        self.hands[player].remove(card)
