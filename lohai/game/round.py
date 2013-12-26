# most recent giver taker wins?
import copy

import lohai.exception
import lohai.game.deck


class Round(object):
    def __init__(self, deck, hands, trump_card):
        self.deck = deck
        self.hands = hands
        self.trump_card = trump_card
        self.pointvalue = trump_card.pointvalue
        self.trump_suit = trump_card.suit
        self.lead_suit = None

        self.player_count = 4
        self.first_player = 0
        self.cur_player = 0

        self.this_rounds_cards = [None] * self.player_count
        self.tricks_won = [0] * self.player_count
        self.most_recent_giver_taker = None
        self.need_giver_input = False

    @staticmethod
    def start_new_round():
        deck = lohai.game.deck.Deck.shuffle_new_deck()

        hands = [list(), list(), list(), list()]

        handsize = 9
        for _i in range(handsize):
            for hand in hands:
                hand.append(deck.draw_card())

        trump_card = deck.draw_card()

        return Round(deck, hands, trump_card)

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

        if card.is_special:
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

        if self.this_rounds_cards[self.cur_player] is not None:
            raise lohai.exception.NotYourTurn("You have already played a card")

        self._is_valid_play(player, card)

        self._play_card(player, card)

    def _play_card(self, player, card):
        self.hands[player].remove(card)

        self.this_rounds_cards[player] = card

        if card.is_mover():
            if self.player_can_mover(player):
                # TODO: Signal we need to move tricks
                return

            # can't use the mover, play from the deck
            self._play_from_deck(player)

        if card.is_shaker():
            if not len(filter(None, self.this_rounds_cards)) > 1:
                # no other cards on the field, play from deck
                self._play_from_deck(player)
            else:
                # Signal we need to shake a card
                return

        if card.is_taker() or card.is_giver():
            self.most_recent_giver_taker = card, player

        if self.lead_suit is None and not card.is_special:
            self.lead_suit = card.suit

        self.cur_player = (self.cur_player + 1) % self.player_count

        if None not in self.this_rounds_cards:
            self._process_trick_winner()

    def _start_new_trick(self, first_player):
        self.this_rounds_cards = [None] * self.player_count
        self.most_recent_giver_taker = None
        self.need_giver_input = False
        self.first_player = self.cur_player = first_player

    def _process_trick_winner(self):
        # did any players play a taker or giver
        if self.most_recent_giver_taker is not None:
            card, player = self.most_recent_giver_taker
            if card.is_taker():
                self.tricks_won[player] += 1
                self._start_new_trick(player)
            elif card.is_giver():
                self.need_giver_input = True
                # TODO: observer here
            else:
                raise Exception("Card %s is not a giver or taker" % card)

            return

        # find the player with the highest trump card or highest lead card
        def _card_key(card):
            value = card.value
            if card.suit == self.trump_suit:
                value += 200
            elif card.suit == self.lead_suit:
                value += 100

            return value

        win_card = sorted(self.this_rounds_cards, key=_card_key)[-1]
        winner = self.this_rounds_cards.index(win_card)
        self.tricks_won[winner] += 1
        self._start_new_trick(winner)

    def handle_shaker(self, player, victim):
        if not self.this_rounds_cards[player].is_shaker():
            raise lohai.exception.InvalidMove(
                "Player %d hasn't played a shaker" % player)
        if self.this_rounds_cards[victim] is None:
            raise lohai.exception.InvalidMove(
                "Cannot steal from player %d, no card" % victim)

        self.this_rounds_cards[player] = self.this_rounds_cards[victim]
        self.this_rounds_cards[victim] = None
        self._play_from_deck(victim)

    def handle_giver(self, victim):
        if not self.need_giver_input:
            raise lohai.exception.InvalidMove("Giver input not expected")

        _card, player = self.most_recent_giver_taker

        if player == victim:
            raise lohai.exception.InvalidMove("Not allowed to give to self")

        self.tricks_won[victim] += 1
        self._start_new_trick(victim)

    def handle_mover(self, player, source, dest):
        if not self.this_rounds_cards[player].is_mover():
            raise lohai.exception.InvalidMove(
                "Player %d doesn't have a mover on the board" % player)

        if self.tricks_won[source] < 1:
            raise lohai.exception.InvalidMove(
                "Cannot steal a trick from a player without tricks")

        self.tricks_won[source] -= 1
        self.tricks_won[dest] += 1

        self._play_from_deck(player)
