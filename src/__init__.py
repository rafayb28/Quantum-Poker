"""
Quantum Poker - A poker game with quantum mechanics

This package contains the core game logic, quantum circuit management,
and API structure for the Quantum Poker game.
"""

from .card import Card, SUITS, RANKS
from .player import Player
from .quantum_circuit import QuantumPokerCircuit
from .game import QuantumPoker

__all__ = [
    "Card",
    "SUITS",
    "RANKS",
    "Player",
    "QuantumPokerCircuit",
    "QuantumPoker",
]

__version__ = "0.1.0"
