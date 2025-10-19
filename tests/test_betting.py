"""
Tests for betting rounds and quantum action integration
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game import QuantumPoker
from src.player import Player


def test_player_betting_actions():
    """Test player betting methods."""
    player = Player("Test Player", 1, starting_chips=1000)

    # Test bet
    amount = player.bet(100)
    assert amount == 100
    assert player.chips == 900
    assert player.current_bet == 100

    # Test call
    amount = player.call(50)
    assert amount == 50
    assert player.chips == 850
    assert player.current_bet == 150

    # Test all-in
    amount = player.bet(850)
    assert amount == 850
    assert player.chips == 0
    assert player.all_in == True

    print("✓ Player betting actions test passed")


def test_player_quantum_chips():
    """Test quantum chip usage."""
    player = Player("Test Player", 1)

    assert player.quantum_chips == 5

    # Use quantum chip
    success = player.use_quantum_chip()
    assert success == True
    assert player.quantum_chips == 4

    # Use all chips
    for _ in range(4):
        player.use_quantum_chip()

    assert player.quantum_chips == 0

    # Try to use when none left
    success = player.use_quantum_chip()
    assert success == False

    print("✓ Quantum chip test passed")


def test_blinds_posting():
    """Test blind posting."""
    game = QuantumPoker(num_players=3)

    # Post blinds
    game.post_blinds(small_blind=10, big_blind=20)

    # Check small blind
    sb_player = game.players[(game.dealer_position + 1) % 3]
    assert sb_player.current_bet == 10

    # Check big blind
    bb_player = game.players[(game.dealer_position + 2) % 3]
    assert bb_player.current_bet == 20

    # Check pot
    assert game.pot == 30
    assert game.current_bet == 20

    print("✓ Blinds posting test passed")


def test_game_state_serialization():
    """Test game state to_dict method."""
    game = QuantumPoker(num_players=2)
    game.deal_hole_cards()

    # Get full state
    state = game.to_dict()
    assert "round" in state
    assert "pot" in state
    assert "players" in state
    assert len(state["players"]) == 2

    # Check player-specific view (hide opponent cards)
    state_p1 = game.to_dict(viewing_player=1)
    assert state_p1["players"][0]["hand"] is not None  # Player 1's cards visible
    assert state_p1["players"][1]["hand"] is None  # Player 2's cards hidden

    print("✓ Game state serialization test passed")


def test_quantum_action_during_betting():
    """Test quantum entanglement during betting round."""
    game = QuantumPoker(num_players=2)
    game.deal_hole_cards()
    game.deal_flop()

    player = game.players[0]
    initial_quantum_chips = player.quantum_chips

    # Perform quantum action
    action = {
        "type": "quantum",
        "source_card_idx": 0,
        "target_card_id": "F0",
        "bit_index": 1,
    }

    game._handle_quantum_action(player, action)

    # Check quantum chip was used
    assert player.quantum_chips == initial_quantum_chips - 1

    # Check entanglement was recorded
    entanglements = game.qc_manager.get_entanglement_graph()
    assert len(entanglements) > 0

    print("✓ Quantum action during betting test passed")


def test_full_hand_with_betting():
    """Test a complete hand with betting rounds."""
    game = QuantumPoker(num_players=2)

    # Override player action to avoid infinite loop
    def mock_action(player, amount_to_call):
        if amount_to_call == 0:
            return {"type": "check"}
        else:
            return {"type": "call"}

    game._get_player_action = mock_action

    # Play hand
    initial_chips_p1 = game.players[0].chips
    initial_chips_p2 = game.players[1].chips

    # Just test that the hand completes without errors
    try:
        result = game.play_hand(small_blind=10, big_blind=20)
        print(f"✓ Full hand completed: {result}")
    except Exception as e:
        print(f"✗ Full hand test failed: {e}")
        raise


if __name__ == "__main__":
    print("Running betting system tests...\n")

    test_player_betting_actions()
    test_player_quantum_chips()
    test_blinds_posting()
    test_game_state_serialization()
    test_quantum_action_during_betting()
    test_full_hand_with_betting()

    print("\n✓ All betting tests passed!")
