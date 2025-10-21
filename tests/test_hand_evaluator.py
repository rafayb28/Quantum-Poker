"""
Tests for poker hand evaluation
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.hand_evaluator import HandEvaluator, HAND_RANKINGS
from src.card import Card


def test_high_card():
    """Test high card evaluation."""
    cards = [
        Card("Hearts", "Ace"),
        Card("Diamonds", "King"),
        Card("Clubs", "10"),
        Card("Spades", "7"),
        Card("Hearts", "2"),
    ]
    hand_name, kickers = HandEvaluator.evaluate_hand(cards)
    assert hand_name == "High Card"
    assert kickers == [14, 13, 10, 7, 2]
    print("✓ High card test passed")


def test_one_pair():
    """Test one pair evaluation."""
    cards = [
        Card("Hearts", "Ace"),
        Card("Diamonds", "Ace"),
        Card("Clubs", "10"),
        Card("Spades", "7"),
        Card("Hearts", "2"),
    ]
    hand_name, kickers = HandEvaluator.evaluate_hand(cards)
    assert hand_name == "One Pair"
    assert kickers[0] == 14  # Pair of aces
    print("✓ One pair test passed")


def test_two_pair():
    """Test two pair evaluation."""
    cards = [
        Card("Hearts", "Ace"),
        Card("Diamonds", "Ace"),
        Card("Clubs", "King"),
        Card("Spades", "King"),
        Card("Hearts", "2"),
    ]
    hand_name, kickers = HandEvaluator.evaluate_hand(cards)
    assert hand_name == "Two Pair"
    assert kickers == [14, 13, 2]  # Aces, Kings, 2 kicker
    print("✓ Two pair test passed")


def test_three_of_a_kind():
    """Test three of a kind evaluation."""
    cards = [
        Card("Hearts", "10"),
        Card("Diamonds", "10"),
        Card("Clubs", "10"),
        Card("Spades", "King"),
        Card("Hearts", "2"),
    ]
    hand_name, kickers = HandEvaluator.evaluate_hand(cards)
    assert hand_name == "Three of a Kind"
    assert kickers[0] == 10
    print("✓ Three of a kind test passed")


def test_straight():
    """Test straight evaluation."""
    cards = [
        Card("Hearts", "9"),
        Card("Diamonds", "8"),
        Card("Clubs", "7"),
        Card("Spades", "6"),
        Card("Hearts", "5"),
    ]
    hand_name, kickers = HandEvaluator.evaluate_hand(cards)
    assert hand_name == "Straight"
    assert kickers == [9]  # 9-high straight
    print("✓ Straight test passed")


def test_wheel_straight():
    """Test A-2-3-4-5 straight (wheel)."""
    cards = [
        Card("Hearts", "Ace"),
        Card("Diamonds", "2"),
        Card("Clubs", "3"),
        Card("Spades", "4"),
        Card("Hearts", "5"),
    ]
    hand_name, kickers = HandEvaluator.evaluate_hand(cards)
    assert hand_name == "Straight"
    assert kickers == [5]  # 5-high (ace is low)
    print("✓ Wheel straight test passed")


def test_flush():
    """Test flush evaluation."""
    cards = [
        Card("Hearts", "Ace"),
        Card("Hearts", "King"),
        Card("Hearts", "9"),
        Card("Hearts", "5"),
        Card("Hearts", "2"),
    ]
    hand_name, kickers = HandEvaluator.evaluate_hand(cards)
    assert hand_name == "Flush"
    assert kickers == [14, 13, 9, 5, 2]
    print("✓ Flush test passed")


def test_full_house():
    """Test full house evaluation."""
    cards = [
        Card("Hearts", "Ace"),
        Card("Diamonds", "Ace"),
        Card("Clubs", "Ace"),
        Card("Spades", "King"),
        Card("Hearts", "King"),
    ]
    hand_name, kickers = HandEvaluator.evaluate_hand(cards)
    assert hand_name == "Full House"
    assert kickers == [14, 13]  # Aces full of Kings
    print("✓ Full house test passed")


def test_four_of_a_kind():
    """Test four of a kind evaluation."""
    cards = [
        Card("Hearts", "7"),
        Card("Diamonds", "7"),
        Card("Clubs", "7"),
        Card("Spades", "7"),
        Card("Hearts", "Ace"),
    ]
    hand_name, kickers = HandEvaluator.evaluate_hand(cards)
    assert hand_name == "Four of a Kind"
    assert kickers == [7, 14]  # Four 7s, Ace kicker
    print("✓ Four of a kind test passed")


def test_straight_flush():
    """Test straight flush evaluation."""
    cards = [
        Card("Hearts", "9"),
        Card("Hearts", "8"),
        Card("Hearts", "7"),
        Card("Hearts", "6"),
        Card("Hearts", "5"),
    ]
    hand_name, kickers = HandEvaluator.evaluate_hand(cards)
    assert hand_name == "Straight Flush"
    assert kickers == [9]
    print("✓ Straight flush test passed")


def test_royal_flush():
    """Test royal flush evaluation."""
    cards = [
        Card("Spades", "Ace"),
        Card("Spades", "King"),
        Card("Spades", "Queen"),
        Card("Spades", "Jack"),
        Card("Spades", "10"),
    ]
    hand_name, kickers = HandEvaluator.evaluate_hand(cards)
    assert hand_name == "Royal Flush"
    assert kickers == [14]
    print("✓ Royal flush test passed")


def test_compare_hands():
    """Test hand comparison."""
    # Flush beats straight
    flush = ("Flush", [14, 10, 8, 5, 2])
    straight = ("Straight", [9])
    assert HandEvaluator.compare_hands(flush, straight) == 1
    assert HandEvaluator.compare_hands(straight, flush) == -1

    # Higher pair wins
    pair_aces = ("One Pair", [14, 10, 8, 5])
    pair_kings = ("One Pair", [13, 10, 8, 5])
    assert HandEvaluator.compare_hands(pair_aces, pair_kings) == 1

    # Kicker matters
    pair_aces_high = ("One Pair", [14, 13, 10, 8])
    pair_aces_low = ("One Pair", [14, 12, 10, 8])
    assert HandEvaluator.compare_hands(pair_aces_high, pair_aces_low) == 1

    print("✓ Hand comparison test passed")


def test_best_hand_from_seven():
    """Test finding best 5-card hand from 7 cards."""
    # Player has pair of 5s, board has pair of Kings
    # Best hand should be two pair: Kings and 5s
    cards = [
        Card("Hearts", "5"),
        Card("Diamonds", "5"),
        Card("Clubs", "King"),
        Card("Spades", "King"),
        Card("Hearts", "Ace"),
        Card("Diamonds", "7"),
        Card("Clubs", "2"),
    ]
    hand_name, kickers = HandEvaluator.evaluate_hand(cards)
    assert hand_name == "Two Pair"
    assert kickers[0] == 13  # Kings
    assert kickers[1] == 5  # 5s
    assert kickers[2] == 14  # Ace kicker
    print("✓ Best hand from 7 cards test passed")


def test_get_best_hand():
    """Test get_best_hand method with separate player and community cards."""
    player_cards = [Card("Hearts", "Ace"), Card("Diamonds", "Ace")]
    community_cards = [
        Card("Clubs", "King"),
        Card("Spades", "King"),
        Card("Hearts", "2"),
        Card("Diamonds", "7"),
        Card("Clubs", "9"),
    ]

    hand_name, kickers, best_cards = HandEvaluator.get_best_hand(
        player_cards, community_cards
    )
    assert hand_name == "Two Pair"
    assert kickers[0] == 14  # Aces
    assert kickers[1] == 13  # Kings
    assert len(best_cards) == 5
    print("✓ Get best hand test passed")


if __name__ == "__main__":
    print("Running hand evaluator tests...\n")

    test_high_card()
    test_one_pair()
    test_two_pair()
    test_three_of_a_kind()
    test_straight()
    test_wheel_straight()
    test_flush()
    test_full_house()
    test_four_of_a_kind()
    test_straight_flush()
    test_royal_flush()
    test_compare_hands()
    test_best_hand_from_seven()
    test_get_best_hand()

    print("\n✓ All hand evaluator tests passed!")
