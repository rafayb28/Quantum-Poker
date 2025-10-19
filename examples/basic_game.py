"""
Example: Basic Quantum Poker Game

This example demonstrates how to use the Quantum Poker library
to create a simple 2-player game with entanglement.
"""

import sys

sys.path.insert(0, "..")

from src import QuantumPoker


def basic_example():
    """Simple 2-player game with one entanglement."""
    print("=== Basic Quantum Poker Example ===\n")

    # Create a 2-player game
    game = QuantumPoker(num_players=2)

    # Deal hole cards
    print("Dealing hole cards...")
    game.deal_hole_cards()

    # Deal flop
    print("Dealing flop...")
    game.deal_flop()

    # Player 1 entangles their first card with first flop card
    print("\nPlayer 1 entangles their card...")
    game.entangle_cards(
        player=game.players[0],
        source_card_idx=0,
        target_card_id="F0",
        bit_index=1,  # ±2 rank variation
    )

    # Deal turn and river
    print("\nDealing turn and river...")
    game.deal_turn()
    game.deal_river()

    # Showdown
    print("\n" + "=" * 50)
    result = game.showdown()

    print("\n" + "=" * 50)
    print("Game complete!")
    return result


if __name__ == "__main__":
    basic_example()
