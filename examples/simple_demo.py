import qiskit
import random

from src.card import Card, SUITS, RANKS
from src.player import Player


class Poker:
    def __init__(self, num_players: int):
        QC = qiskit.QuantumCircuit()
        self.cards = [Card(suit, rank) for suit in SUITS for rank in RANKS]
        self.players = [Player(f"Player {i+1}", i + 1) for i in range(num_players)]
        self.dealt = 0
        self.shuffle()

        for card in self.cards:  # add to circuit
            QC.add_register(card.register)
            card.prepare(QC)
            print(card.__repr__())

    def shuffle(self):
        random.shuffle(self.cards)

    def deal_hand(self):
        for player in self.players:
            player.hand = [self.cards[self.dealt], self.cards[self.dealt + 1]]
            self.dealt += 2


if __name__ == "__main__":
    poker_game = Poker(num_players=2)
