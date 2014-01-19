# most recent giver taker wins?
from collections import namedtuple

import copy

import lohai.exception
import lohai.events
import lohai.game.deck

from lohai.events import Events, event_notify
from lohai.game.deck import CardValue, SpecialCard


CardPlayer = namedtuple('CardPlayer',  # pylint: disable=C0103
                        ['card', 'player'])


class Hand(object):
    """ A single hand of a Lohai round (also known as a Trick)

    This object tracks:
        - The cards played on the field
        - Who played the most recent Giver/Taker
        - The lead suit for the hand
        - Which player went first (canonically in the Round)
        - Which player is expected to go next
        - Calculating the hand winner at the end of the round
    """
    def __init__(self, round, first_player):
        self.round = round
        self.most_recent_giver_taker = None
        self.lead_suit = None
        self.first_player = self.cur_player = first_player
        self.field_cards = [None] * self.round.player_count

    def _is_valid_play(self, player, card):
        if not self.round.player_has_card(player, card):
            raise lohai.exception.InvalidCard(
                "Card %s is not in player %s's hand" % (card, player))

        if card.is_special:
            return

        if (self.lead_suit is not None
              and card.suit != self.lead_suit
              and self.round.player_has_suit(player, self.lead_suit)):
            raise lohai.exception.InvalidCard("Must play a lead suit card")

    def _send_event_for_player(self, player, event):
        event_notify(self.round.game_id,
                     self.round.id_for_player(player),
                     event)

    def _play_card_from_deck(self, player):
        self._play_card_to_field(player, self.round.draw_card())

    def _play_card_to_field(self, player, card):
        self.field_cards[player] = card

        if card.value is CardValue.mover:
            if self.round.player_can_mover(player):
                self._send_event_for_player(player, Events.mover_input_needed)
                return

            # can't use the mover, play from the deck
            self._play_card_from_deck(player)

        if card.value is CardValue.shaker:
            if not len(filter(None, self.field_cards)) > 1:
                # no other cards on the field, play from deck
                self._play_card_from_deck(player)
            else:
                # Signal we need to shake a card
                self._send_event_for_player(player, Events.shaker_input_needed)
                return

        if card.value in (CardValue.taker, CardValue.giver):
            self.most_recent_giver_taker = CardPlayer(card, player)

        if self.lead_suit is None and not card.is_special:
            self.lead_suit = card.suit

        self.cur_player = (self.cur_player + 1) % self.round.player_count

    def hand_complete(self):
        return (None not in self.field_cards
                and SpecialCard(CardValue.shaker) not in self.field_cards
                and SpecialCard(CardValue.mover) not in self.field_cards)

    def play_card(self, player, card):
        if self.cur_player != player:
            raise lohai.exception.NotYourTurn("Not player number %s turn"
                                              % player)

        if self.field_cards[self.cur_player] is not None:
            raise lohai.exception.InvalidMove("You have already played a card")

        self._is_valid_play(player, card)

        self.round.remove_card_from_hand(player, card)

        self._play_card_to_field(player, card)

    def handle_mover(self, player, source, dest):
        if not self.field_cards[player].value is CardValue.mover:
            raise lohai.exception.InvalidMove(
                "Player %d doesn't have a mover on the board" % player)

        self.round.transfer_trick(source, dest)

        self._play_card_from_deck(player)

    def handle_shaker(self, player, victim):
        if not self.field_cards[player].value is CardValue.shaker:
            raise lohai.exception.InvalidMove(
                "Player %d hasn't played a shaker" % player)

        if self.field_cards[victim] is None:
            raise lohai.exception.InvalidMove(
                "Cannot steal from player %d, no card" % victim)

        self.field_cards[player] = self.field_cards[victim]
        self.field_cards[victim] = None
        self._play_card_from_deck(victim)

    def verify_giver_ok(self, player, victim):
        if not self.hand_complete():
            raise lohai.exception.InvalidMove("Round is not yet over")

        if self.most_recent_giver_taker is None:
            raise lohai.exception.InvalidMove("No giver has been played")

        if self.most_recent_giver_taker.player != player:
            raise lohai.exception.InvalidMove(
                "Player %s is not eligible to play a giver", player)

        if self.most_recent_giver_taker.card.value != CardValue.giver:
            raise lohai.exception.InvalidMove(
                "Player %s did not play a giver", player)

        if player == victim:
            raise lohai.exception.InvalidMove("Not allowed to give to self")

    def process_trick_winner(self):
        # did any players play a taker or giver
        if self.most_recent_giver_taker is not None:
            card, player = self.most_recent_giver_taker
            if card.value is CardValue.taker:
                return player
            elif card.value is CardValue.giver:
                self._send_event_for_player(player, Events.giver_input_needed)
                return
            else:
                raise Exception("Card %s is not a giver or taker" % card)

        # find the player with the highest trump card or highest lead card
        def _card_key(card):
            value = card.value
            if card.suit == self.round.trump_suit:
                value += 200
            elif card.suit == self.lead_suit:
                value += 100

            return value

        win_card = sorted(self.field_cards, key=_card_key)[-1]
        winner = self.field_cards.index(win_card)
        return winner


class Round(object):
    """ A round of Lohai, consisting of nine Hands

    This object tracks:
        - The cards in players' hands
        - The deck of remaining cards
        - The trump card for the round
        - The pointvalue of the round
        - The player who lead the most recent hand
        - The trick count for each player
    """
    def __init__(self, deck, hands, trump_card):
        self.deck = deck
        self.hands = hands
        self.trump_card = trump_card
        self.pointvalue = trump_card.pointvalue
        self.trump_suit = trump_card.suit

        self._player_count = 4
        self.first_player = 0

        self.tricks_won = [0] * self.player_count
        self.most_recent_giver_taker = None
        self.need_giver_input = False

        self.current_hand = None
        self._start_new_trick(self.first_player)

    # transition API
    @property
    def this_rounds_cards(self):
        return self.current_hand.field_cards

    def _set_cur_player(self, player):
        self.current_hand.cur_player = player

    cur_player = property(lambda self: None, _set_cur_player)

    # end transition API

    # public API for Hand

    game_id = -1

    @staticmethod
    def id_for_player(player):
        return player

    def draw_card(self):
        return self.deck.draw_card()

    @property
    def player_count(self):
        return self._player_count

    def player_has_card(self, player, card):
        return card in self.get_hand_for_player(player)

    def player_has_suit(self, player, suit):
        player_hand = self.get_hand_for_player(player)
        player_suits = set([card.suit for card in player_hand])
        return suit in player_suits

    def remove_card_from_hand(self, player, card):
        if not self.player_has_card(player, card):
            raise lohai.exception.InvalidCard(
                "Card %s is not in player %s's hand" % (card, player))

        self.hands[player].remove(card)

    def get_hand_for_player(self, player):
        return copy.deepcopy(self.hands[player])

    # end Hand API

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

    def player_can_mover(self, player):
        """ A player can use the special portion of a mover card iff they are
        definitively in the middle
        """
        player_score = self.tricks_won[player]
        min_score = min(self.tricks_won)
        max_score = max(self.tricks_won)

        return min_score < player_score and player_score < max_score

    def play_card(self, player, card):
        self.current_hand.play_card(player, card)

        if self.current_hand.hand_complete():
            self._process_trick_winner()

    def _start_new_trick(self, first_player):
        self.current_hand = Hand(self, first_player)

    def _process_trick_winner(self):
        winner = self.current_hand.process_trick_winner()
        if winner:
            self.tricks_won[winner] += 1
            self._start_new_trick(winner)

    def handle_shaker(self, player, victim):
        self.current_hand.handle_shaker(player, victim)

    def handle_giver(self, player, victim):
        self.current_hand.verify_giver_ok(player, victim)

        self.tricks_won[victim] += 1
        self._start_new_trick(victim)

    def handle_mover(self, player, source, dest):
        self.current_hand.handle_mover(player, source, dest)

    def transfer_trick(self, source, dest):
        if self.tricks_won[source] < 1:
            raise lohai.exception.InvalidMove(
                "Cannot steal a trick from a player without tricks")

        self.tricks_won[source] -= 1
        self.tricks_won[dest] += 1
