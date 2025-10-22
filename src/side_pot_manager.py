"""
Side pot management for all-in scenarios
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Pot:
    """Represents a pot (main or side) in the game."""

    amount: int
    eligible_players: List[int]  # Player numbers eligible to win this pot

    def __repr__(self):
        return f"Pot({self.amount} chips, players {self.eligible_players})"


class SidePotManager:
    """Manages main pot and side pots for all-in scenarios."""

    def __init__(self):
        self.pots: List[Pot] = []

    def calculate_pots(self, players_bets: Dict[int, Tuple[int, bool]]) -> List[Pot]:
        """
        Calculate main pot and side pots based on player bets.

        Args:
            players_bets: Dict of {player_number: (bet_amount, is_all_in)}

        Returns:
            List of Pot objects from main to side pots
        """
        if not players_bets:
            return []

        # Sort players by bet amount
        sorted_players = sorted(players_bets.items(), key=lambda x: x[1][0])

        pots = []
        previous_level = 0
        remaining_players = set(players_bets.keys())

        for player_num, (bet_amount, is_all_in) in sorted_players:
            if bet_amount > previous_level:
                # Create pot for this level
                pot_contribution = bet_amount - previous_level
                pot_amount = pot_contribution * len(remaining_players)

                pots.append(
                    Pot(
                        amount=pot_amount,
                        eligible_players=sorted(list(remaining_players)),
                    )
                )

                previous_level = bet_amount

            # If player is all-in, they can't win higher pots
            if is_all_in:
                remaining_players.discard(player_num)

        self.pots = pots
        return pots

    def get_total_pot(self) -> int:
        """Get total amount across all pots."""
        return sum(pot.amount for pot in self.pots)

    def award_pots(
        self, player_hands: Dict[int, Tuple[str, List[int]]]
    ) -> Dict[int, int]:
        """
        Award pots to winners based on hand rankings.

        Args:
            player_hands: Dict of {player_number: (hand_name, kickers)}

        Returns:
            Dict of {player_number: total_winnings}
        """
        from .hand_evaluator import HandEvaluator

        winnings = {player_num: 0 for player_num in player_hands.keys()}

        for pot in self.pots:
            # Filter eligible players who haven't folded
            eligible_hands = {
                p: hand for p, hand in player_hands.items() if p in pot.eligible_players
            }

            if not eligible_hands:
                continue

            # Find winner(s) of this pot
            best_hand = None
            winners = []

            for player_num, hand in eligible_hands.items():
                if best_hand is None:
                    best_hand = hand
                    winners = [player_num]
                else:
                    comparison = HandEvaluator.compare_hands(hand, best_hand)
                    if comparison > 0:
                        best_hand = hand
                        winners = [player_num]
                    elif comparison == 0:
                        winners.append(player_num)

            # Split pot among winners
            pot_share = pot.amount // len(winners)
            for winner in winners:
                winnings[winner] += pot_share

        return winnings

    def get_pot_display(self) -> List[str]:
        """Get human-readable pot information."""
        if not self.pots:
            return ["No pots"]

        displays = []
        for i, pot in enumerate(self.pots):
            pot_type = "Main Pot" if i == 0 else f"Side Pot {i}"
            displays.append(
                f"{pot_type}: {pot.amount} chips (Players {', '.join(map(str, pot.eligible_players))})"
            )
        return displays

    def clear(self):
        """Clear all pots."""
        self.pots = []


def example_side_pot_calculation():
    """Example demonstrating side pot calculation."""
    print("=== Side Pot Calculation Example ===\n")

    manager = SidePotManager()

    # Example scenario:
    # Player 1: All-in for 100
    # Player 2: Calls 300
    # Player 3: Calls 300

    players_bets = {1: (100, True), 2: (300, False), 3: (300, False)}  # All-in

    pots = manager.calculate_pots(players_bets)

    print("Scenario:")
    print("  Player 1: All-in for 100")
    print("  Player 2: Bet 300")
    print("  Player 3: Bet 300\n")

    print("Pots created:")
    for display in manager.get_pot_display():
        print(f"  {display}")

    print(f"\nTotal pot: {manager.get_total_pot()}")

    # Example 2: Multiple all-ins
    print("\n" + "=" * 50)
    print("\n=== Multiple All-ins Example ===\n")

    manager2 = SidePotManager()

    players_bets2 = {
        1: (50, True),  # All-in for 50
        2: (150, True),  # All-in for 150
        3: (300, False),
        4: (300, False),
    }

    pots2 = manager2.calculate_pots(players_bets2)

    print("Scenario:")
    print("  Player 1: All-in for 50")
    print("  Player 2: All-in for 150")
    print("  Player 3: Bet 300")
    print("  Player 4: Bet 300\n")

    print("Pots created:")
    for display in manager2.get_pot_display():
        print(f"  {display}")

    print(f"\nTotal pot: {manager2.get_total_pot()}")


if __name__ == "__main__":
    example_side_pot_calculation()
