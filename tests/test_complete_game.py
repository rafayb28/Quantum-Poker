"""
Test complete game with hand evaluation and winner determination
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game import QuantumPoker


def test_showdown_with_winner():
    """Test full showdown with hand evaluation."""
    print("Testing showdown with winner determination...\n")

    game = QuantumPoker(num_players=2)

    # Override player action to simple logic
    def mock_action(player, amount_to_call):
        return {"type": "call"} if amount_to_call > 0 else {"type": "check"}

    game._get_player_action = mock_action

    # Deal cards
    game.deal_hole_cards()
    game.post_blinds(ante=10)

    print("Initial chip counts:")
    for p in game.players:
        print(f"  {p.name}: {p.chips} chips")

    # Play through rounds without betting
    game.current_round = "pre-flop"
    game.betting_round("pre-flop")

    game.deal_flop()
    game.betting_round("flop")

    game.deal_turn()
    game.betting_round("turn")

    game.deal_river()
    game.betting_round("river")

    # Showdown
    result = game.showdown()

    print("\nFinal chip counts:")
    for p in game.players:
        print(f"  {p.name}: {p.chips} chips")

    # Verify winner was determined if no errors
    if not result["has_errors"]:
        assert result["winner_info"] is not None
        assert len(result["winner_info"]["winners"]) >= 1
        print("\n✓ Winner determination successful!")
    else:
        print("\n⚠️ Quantum errors occurred, winner not determined")

    print("\n✓ Showdown test completed")


if __name__ == "__main__":
    print("=" * 50)
    print("COMPLETE GAME TEST WITH HAND EVALUATION")
    print("=" * 50 + "\n")

    test_showdown_with_winner()
