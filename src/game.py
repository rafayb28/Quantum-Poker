"""
Main Poker Game Logic with Quantum Circuit Integration
"""

from typing import List, Optional, Dict
import random

from .card import Card, SUITS, RANKS
from .player import Player
from .quantum_circuit import QuantumPokerCircuit


class QuantumPoker:
    """
    Main game class that manages the poker game with quantum mechanics.
    """

    def __init__(self, num_players: int):
        if num_players < 2 or num_players > 10:
            raise ValueError("Number of players must be between 2 and 10")

        self.num_players = num_players
        self.players: List[Player] = [
            Player(f"Player {i+1}", i + 1) for i in range(num_players)
        ]

        # Initialize quantum circuit manager
        self.qc_manager = QuantumPokerCircuit()

        # Create full deck
        self.deck: List[Card] = []
        for suit in SUITS:
            for rank in RANKS:
                self.deck.append(Card(suit, rank))

        self.shuffle_deck()

        # Community cards
        self.flop: List[Optional[Card]] = [None, None, None]
        self.turn: Optional[Card] = None
        self.river: Optional[Card] = None

        # Game state
        self.current_round = "pre-flop"  # pre-flop, flop, turn, river, showdown
        self.pot = 0
        self.current_bet = 0
        self.dealer_position = 0
        self.current_player_idx = 0

        # Deck index for dealing
        self.deck_index = 0

    def shuffle_deck(self):
        """Shuffle the deck randomly."""
        random.shuffle(self.deck)

    def deal_hole_cards(self):
        """
        Deal two hole cards to each player and add them to the quantum circuit.
        """
        for player in self.players:
            if player.folded:
                continue

            # Deal two cards
            card1 = self.deck[self.deck_index]
            card2 = self.deck[self.deck_index + 1]
            self.deck_index += 2

            # Add to quantum circuit with identifiers
            identifier1 = f"P{player.number}H1"
            identifier2 = f"P{player.number}H2"

            self.qc_manager.add_card(card1, identifier1)
            self.qc_manager.add_card(card2, identifier2)

            # Add to player's hand
            player.hand = [card1, card2]

    def deal_flop(self):
        """
        Deal the flop (3 community cards).
        """
        if self.current_round != "pre-flop":
            raise ValueError("Flop can only be dealt after pre-flop")

        # Burn one card (optional in quantum version, but keeping for tradition)
        self.deck_index += 1

        # Deal 3 cards
        for i in range(3):
            card = self.deck[self.deck_index]
            self.deck_index += 1

            identifier = f"F{i}"
            self.qc_manager.add_card(card, identifier)
            self.flop[i] = card

        self.current_round = "flop"

    def deal_turn(self):
        """
        Deal the turn (4th community card).
        """
        if self.current_round != "flop":
            raise ValueError("Turn can only be dealt after flop")

        # Burn one card
        self.deck_index += 1

        card = self.deck[self.deck_index]
        self.deck_index += 1

        self.qc_manager.add_card(card, "T")
        self.turn = card

        self.current_round = "turn"

    def deal_river(self):
        """
        Deal the river (5th community card).
        """
        if self.current_round != "turn":
            raise ValueError("River can only be dealt after turn")

        # Burn one card
        self.deck_index += 1

        card = self.deck[self.deck_index]
        self.deck_index += 1

        self.qc_manager.add_card(card, "R")
        self.river = card

        self.current_round = "river"

    def entangle_cards(
        self, player: Player, source_card_idx: int, target_card_id: str, bit_index: int
    ):
        """
        Allow a player to entangle one of their cards with another card.

        Args:
            player: The player performing the entanglement
            source_card_idx: Index of player's hole card (0 or 1)
            target_card_id: Identifier of target card (e.g., "F0", "P2H1")
            bit_index: Which rank bit to entangle (0-2 only)
                      0 = ±1 rank, 1 = ±2 rank, 2 = ±4 rank
        """
        if player.quantum_chips <= 0:
            raise ValueError("Player has no quantum chips left")

        if source_card_idx not in [0, 1]:
            raise ValueError("Invalid hole card index")
        
        if bit_index < 0 or bit_index > 2:
            raise ValueError(
                f"Invalid bit index: {bit_index}. Only rank bits 0-2 allowed.\n"
                f"  Bit 0: ±1 rank variation\n"
                f"  Bit 1: ±2 rank variation\n"
                f"  Bit 2: ±4 rank variation"
            )

        # Get source card identifier
        source_card_id = f"P{player.number}H{source_card_idx + 1}"

        # Perform entanglement
        self.qc_manager.entangle_cards(source_card_id, target_card_id, bit_index)

        # Deduct quantum chip
        player.quantum_chips -= 1

        bit_effect = ["±1", "±2", "±4"][bit_index]
        print(
            f"{player.name} entangled {source_card_id} with {target_card_id} "
            f"(bit {bit_index}: {bit_effect} rank change)"
        )

    def betting_round(self):
        """
        Placeholder for betting round logic.
        TODO: Implement full betting logic with fold/check/call/raise.
        """
        # This will be implemented in Phase 2
        pass

    def showdown(self) -> Dict:
        """
        Perform showdown: measure all cards and determine winner.

        Returns:
            Dictionary with simulation results and decoded cards
        """
        print("\n=== SHOWDOWN ===")

        # Measure all cards
        self.qc_manager.measure_all_cards()

        # Run simulation without strict filtering (accept quantum measurement errors as part of gameplay)
        print("Running quantum measurement simulation...")
        results = self.qc_manager.simulate(shots=2048, filter_invalid=False)

        # Get most common outcome
        most_common = max(results.items(), key=lambda x: x[1])
        winning_bitstring = most_common[0]
        total_shots = sum(results.values())

        print(f"Most common outcome: {most_common[1]} shots ({100*most_common[1]/total_shots:.1f}%)\n")

        # Decode all cards
        decoded_cards = {}
        print("Final Card Values:")
        print("-" * 40)
        
        has_invalid = False
        for card_id in self.qc_manager.registered_cards:
            rank, suit = self.qc_manager.decode_measurement(winning_bitstring, card_id)
            
            # Handle invalid measurements as "quantum errors" - re-measure that specific card
            if rank is None or suit is None:
                has_invalid = True
                # For now, just mark as error - in production, could trigger re-measurement
                rank, suit = "ERROR", "ERROR"
            
            decoded_cards[card_id] = (rank, suit)
            
            # Pretty print card type
            if card_id.startswith("P"):
                player_num = card_id[1]
                card_num = card_id[3]
                card_display = f"{rank} of {suit}" if rank != "ERROR" else "⚠️ QUANTUM ERROR"
                print(f"Player {player_num} - Hole Card {card_num}: {card_display}")
            elif card_id.startswith("F"):
                flop_num = int(card_id[1]) + 1
                card_display = f"{rank} of {suit}" if rank != "ERROR" else "⚠️ QUANTUM ERROR"
                print(f"Flop Card {flop_num}: {card_display}")
            elif card_id == "T":
                card_display = f"{rank} of {suit}" if rank != "ERROR" else "⚠️ QUANTUM ERROR"
                print(f"Turn: {card_display}")
            elif card_id == "R":
                card_display = f"{rank} of {suit}" if rank != "ERROR" else "⚠️ QUANTUM ERROR"
                print(f"River: {card_display}")

        if has_invalid:
            print("\n⚠️  Note: Quantum errors occurred due to entanglement creating invalid card states.")
            print("   In a real game, these cards would be re-measured or the hand re-dealt.")

        self.current_round = "showdown"

        return {
            "results": results,
            "winning_bitstring": winning_bitstring,
            "decoded_cards": decoded_cards,
            "total_shots": total_shots,
            "has_errors": has_invalid,
        }

    def get_game_state(self) -> Dict:
        """
        Get current game state for API/frontend consumption.

        Returns:
            Dictionary representing current game state
        """
        return {
            "round": self.current_round,
            "pot": self.pot,
            "current_bet": self.current_bet,
            "players": [
                {
                    "name": p.name,
                    "number": p.number,
                    "chips": p.chips,
                    "quantum_chips": p.quantum_chips,
                    "current_bet": p.current_bet,
                    "folded": p.folded,
                    "hand_identifiers": [
                        f"P{p.number}H1",
                        f"P{p.number}H2",
                    ]
                    if p.hand
                    else [],
                }
                for p in self.players
            ],
            "community_cards": {
                "flop": ["F0", "F1", "F2"] if self.flop[0] else [],
                "turn": "T" if self.turn else None,
                "river": "R" if self.river else None,
            },
            "entanglements": self.qc_manager.get_entanglement_graph(),
        }

    def get_circuit_diagram(self) -> str:
        """
        Get visual representation of the quantum circuit.
        """
        return self.qc_manager.get_circuit_diagram()


def example_game():
    """
    Example game flow demonstrating quantum entanglement.
    """
    print("=== Quantum Poker Example Game ===\n")

    # Create game with 2 players
    game = QuantumPoker(num_players=2)

    # Deal hole cards
    print("Dealing hole cards...")
    game.deal_hole_cards()

    print("\nPlayer hands (identifiers):")
    for player in game.players:
        print(
            f"{player.name}: {player.hand[0].identifier}, {player.hand[1].identifier}"
        )

    # Deal flop
    print("\nDealing flop...")
    game.deal_flop()
    print(f"Flop: {[card.identifier for card in game.flop]}")

    # Player 1 entangles their first card with first flop card (bit 1 - ±2 rank)
    print("\nPlayer 1 performs quantum entanglement...")
    print("  (Entangling rank bit 1 - creates ±2 rank variation)")
    game.entangle_cards(
        player=game.players[0],
        source_card_idx=0,  # First hole card
        target_card_id="F0",  # First flop card
        bit_index=1,  # Bit 1 of rank: ±2 rank variation
    )

    # Deal turn and river
    print("\nDealing turn...")
    game.deal_turn()
    print(f"Turn: {game.turn.identifier}")

    print("\nDealing river...")
    game.deal_river()
    print(f"River: {game.river.identifier}")

    # Player 2 entangles their second card with the river (bit 0 - ±1 rank)
    print("\nPlayer 2 performs quantum entanglement...")
    print("  (Entangling rank bit 0 - creates ±1 rank variation)")
    game.entangle_cards(
        player=game.players[1],
        source_card_idx=1,  # Second hole card
        target_card_id="R",  # River card
        bit_index=0,  # Bit 0 of rank: ±1 rank variation
    )

    # Show circuit diagram
    print("\n=== Quantum Circuit ===")
    print(game.get_circuit_diagram())

    # Showdown
    showdown_results = game.showdown()

    # Show game state
    print("\n=== Final Game State ===")
    import json

    print(json.dumps(game.get_game_state(), indent=2))


if __name__ == "__main__":
    example_game()
