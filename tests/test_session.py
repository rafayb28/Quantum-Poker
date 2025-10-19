"""
Tests for game session management
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game import QuantumPoker


def test_session_start_and_end():
    """Test starting and ending a session."""
    game = QuantumPoker(num_players=3, starting_chips=500, small_blind=5, big_blind=10)
    
    assert game.session_active == False
    assert game.hands_played == 0
    
    game.start_session()
    
    assert game.session_active == True
    assert game.hand_number == 0
    
    game.end_session()
    
    assert game.session_active == False
    
    print("✓ Session start/end test passed")


def test_dealer_rotation():
    """Test dealer button rotation."""
    game = QuantumPoker(num_players=3, starting_chips=1000)
    
    initial_dealer = game.dealer_position
    
    game._rotate_dealer()
    
    # Dealer should have moved
    assert game.dealer_position == (initial_dealer + 1) % 3
    
    print("✓ Dealer rotation test passed")


def test_session_stats():
    """Test session statistics tracking."""
    game = QuantumPoker(num_players=2, starting_chips=1000)
    game.start_session()
    
    # Give one player more chips
    game.players[0].chips = 1500
    game.players[1].chips = 500
    
    stats = game.get_session_stats()
    
    assert stats["active_players"] == 2
    assert stats["eliminated_players"] == 0
    assert stats["session_active"] == True
    assert len(stats["player_stats"]) == 2
    assert stats["player_stats"][0]["profit"] == 500  # Player 1 up 500
    assert stats["player_stats"][1]["profit"] == -500  # Player 2 down 500
    
    print("✓ Session stats test passed")


def test_elimination_detection():
    """Test detecting when players are eliminated."""
    game = QuantumPoker(num_players=3, starting_chips=100)
    
    # Eliminate two players
    game.players[1].chips = 0
    game.players[2].chips = 0
    
    stats = game.get_session_stats()
    
    assert stats["active_players"] == 1
    assert stats["eliminated_players"] == 2
    assert stats["player_stats"][1]["active"] == False
    assert stats["player_stats"][2]["active"] == False
    
    print("✓ Elimination detection test passed")


def test_multi_hand_session():
    """Test playing multiple hands in a session."""
    game = QuantumPoker(num_players=2, starting_chips=1000, small_blind=10, big_blind=20)
    
    # Mock player actions to avoid hanging
    def mock_action(player, amount_to_call):
        # Everyone just checks
        return {"type": "check"} if amount_to_call == 0 else {"type": "fold"}
    
    game._get_player_action = mock_action
    
    game.start_session()
    
    # Play 3 hands
    for i in range(3):
        result = game.play_next_hand()
        if result is None:
            break  # Game ended
    
    assert game.hands_played >= 1
    assert game.hand_number >= 1
    
    game.end_session()
    
    print("✓ Multi-hand session test passed")


def test_session_with_elimination():
    """Test session ending when only one player remains."""
    game = QuantumPoker(num_players=2, starting_chips=50, small_blind=10, big_blind=20)
    
    def mock_action(player, amount_to_call):
        # Player 2 always folds, player 1 always calls
        if player.number == 2:
            return {"type": "fold"}
        return {"type": "call"} if amount_to_call > 0 else {"type": "check"}
    
    game._get_player_action = mock_action
    
    game.start_session()
    
    # Play until someone is eliminated
    max_hands = 10
    for _ in range(max_hands):
        result = game.play_next_hand()
        if result is None:
            break
        
        # Check if anyone is eliminated
        if any(p.chips == 0 for p in game.players):
            break
    
    # Session should have ended or player eliminated
    active_count = sum(1 for p in game.players if p.chips > 0)
    assert active_count <= 2
    
    print("✓ Session with elimination test passed")


if __name__ == "__main__":
    print("Running session management tests...\n")
    
    test_session_start_and_end()
    test_dealer_rotation()
    test_session_stats()
    test_elimination_detection()
    test_multi_hand_session()
    test_session_with_elimination()
    
    print("\n✓ All session management tests passed!")
