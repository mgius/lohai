# most recent giver taker wins?
import copy
import lohai.deck
import lohai.exception


class Round(object):
    def __init__(self, deck, hands, pointvalue, trump_suit):
        self.deck = deck
        self.hands = hands
        self.pointvalue = pointvalue
        self.trump_suit = trump_suit
        self.lead_suit = None

        self.player_count = 4
        self.first_player = 0
        self.cur_player = 0

        self.this_rounds_cards = [None] * self.player_count
        self.tricks_won = [0] * self.player_count
        self.most_recent_giver_taker = None

    @staticmethod
    def start_new_round():
        deck = lohai.deck.Deck.shuffle_new_deck()

        hands = [list(), list(), list(), list()]

        handsize = 9
        for i in range(handsize):
            for hand in hands:
                hand.append(deck.draw_card())

        trump_card = deck.draw_card()
        if trump_card.is_special():
            # if a special card is turned, there is no trump for the hand
            trump_suit = lohai.deck.Suit.none
        else:
            trump_suit = trump_card.suit

        return Round(deck, hands, trump_card.pointvalue, trump_suit)

    def get_hand_for_player(self, player):
        return copy.deepcopy(self.hands[player])

    def player_can_mover(self, player):
        """ A player can use the special portion of a mover card iff they are
        definitively in the middle
        """
        player_score = self.tricks_won[player]
        min_score = min(self.tricks_won)
        max_score = max(self.tricks_won)

        return min_score < player_score and player_score < max_score

    def _play_from_deck(self, player):
        card = self.deck.draw_card()
        self.hands[player].append(card)
        self._play_card(player, card)

    def _is_valid_play(self, player, card):
        player_hand = self.get_hand_for_player(player)
        if card not in player_hand:
            raise lohai.exception.InvalidCard(
                "Card %s is not in player %s's hand" % (card, player))

        if card.is_special():
            return

        if self.lead_suit is not None and card.suit != self.lead_suit:
            player_hand = self.get_hand_for_player(player)
            player_suits = set([card.suit for card in player_hand])
            if self.lead_suit in player_suits:
                raise lohai.exception.InvalidCard("Must play a lead suit card")

    def play_card(self, player, card):
        if self.cur_player != player:
            raise lohai.exception.NotYourTurn("Not player number %s turn"
                                              % player)

        self._is_valid_play(player, card)

        self._play_card(player, card)

    def _play_card(self, player, card):
        self.hands[player].remove(card)

        # play the card to the field
        self.this_rounds_cards[player] = card

        if card.is_mover():
            if self.player_can_mover(player):
                # Signal we need to move tricks
                raise NeedMoverInput

            # can't use the mover, play from the deck
            self._play_from_deck(player)

        if card.is_shaker():
            if not filter(None, self.this_rounds_cards):
                # no other cards on the field, play from deck
                self._play_from_deck(player)
            else:
                # Signal we need to shake a card
                raise NeedShakerInput

        if card.is_taker() or card.is_giver():
            self.most_recent_giver_taker = player

        if self.lead_suit is None and not card.is_special():
            self.lead_suit = card.suit

        self.cur_player = (self.cur_player + 1) % self.player_count

        if None not in self.this_rounds_cards:
            self._process_round_winner()

    def _process_round_winner(self):
        # find the player with the highest lead card
        cur_card = self.this_rounds_cards[self.first_player]
        for card in self.this_rounds_cards:
            if card.suit == self.lead_suit and card > cur_card:
                cur_card = card

        winner = self.this_rounds_cards.index(cur_card)
        self.tricks_won[winner] += 1

    def handle_shaker(self, player, victim):
        if not self.this_rounds_cards[player].is_shaker():
            raise Exception("Player %d hasn't played a shaker" % player)
        if self.this_rounds_cards[victim] is None:
            raise Exception("Cannot steal from player %d, no card" % victim)

        self.this_rounds_cards[player] = self.this_rounds_cards[victim]
        self.this_rounds_cards[victim] = None
        self._play_from_deck(victim)
