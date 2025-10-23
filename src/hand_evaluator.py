"""
Poker hand evaluation system
Ranks hands from high card to royal flush
"""

from typing import List, Tuple, Dict
from collections import Counter
from .card import Card


# Hand rankings (higher = better)
HAND_RANKINGS = {
    "High Card": 1,
    "One Pair": 2,
    "Two Pair": 3,
    "Three of a Kind": 4,
    "Straight": 5,
    "Flush": 6,
    "Full House": 7,
    "Four of a Kind": 8,
    "Straight Flush": 9,
    "Royal Flush": 10,
}


# Convert rank strings to numeric values for comparison
RANK_VALUES = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "Jack": 11,
    "Queen": 12,
    "King": 13,
    "Ace": 14,
}


# Suit rankings for tie-breaking (Spades highest, Clubs lowest)
SUIT_VALUES = {
    "Spades": 4,
    "Hearts": 3,
    "Diamonds": 2,
    "Clubs": 1,
}


class HandEvaluator:
    """Evaluates poker hands and determines winners."""

    @staticmethod
    def evaluate_hand(cards: List[Card]) -> Tuple[str, List[int]]:
        """
        Evaluate a 5-7 card poker hand.

        Args:
            cards: List of Card objects

        Returns:
            Tuple of (hand_name, kickers) where kickers are sorted values for tiebreaking
        """
        if len(cards) < 5:
            raise ValueError("Need at least 5 cards to evaluate hand")

        # Get best 5-card combination
        if len(cards) == 5:
            return HandEvaluator._evaluate_five_cards(cards)
        else:
            # Try all 5-card combinations and return best
            from itertools import combinations

            best_hand = ("High Card", [2])
            best_rank = HAND_RANKINGS[best_hand[0]]

            for combo in combinations(cards, 5):
                hand_name, kickers = HandEvaluator._evaluate_five_cards(list(combo))
                hand_rank = HAND_RANKINGS[hand_name]

                if hand_rank > best_rank or (
                    hand_rank == best_rank and kickers > best_hand[1]
                ):
                    best_hand = (hand_name, kickers)
                    best_rank = hand_rank

            return best_hand

    @staticmethod
    def _evaluate_five_cards(cards: List[Card]) -> Tuple[str, List[int]]:
        """Evaluate exactly 5 cards."""
        ranks = [RANK_VALUES[card.rank] for card in cards]
        suits = [card.suit for card in cards]

        rank_counts = Counter(ranks)
        is_flush = len(set(suits)) == 1
        is_straight, straight_high = HandEvaluator._check_straight(ranks)

        # Count rank frequencies
        counts = sorted(rank_counts.values(), reverse=True)
        unique_ranks = sorted(rank_counts.keys(), reverse=True)

        # Royal Flush
        if is_flush and is_straight and straight_high == 14:
            return ("Royal Flush", [14])

        # Straight Flush
        if is_flush and is_straight:
            return ("Straight Flush", [straight_high])

        # Four of a Kind
        if counts == [4, 1]:
            four_kind = [r for r, c in rank_counts.items() if c == 4][0]
            kicker = [r for r, c in rank_counts.items() if c == 1][0]
            return ("Four of a Kind", [four_kind, kicker])

        # Full House
        if counts == [3, 2]:
            three_kind = [r for r, c in rank_counts.items() if c == 3][0]
            pair = [r for r, c in rank_counts.items() if c == 2][0]
            return ("Full House", [three_kind, pair])

        # Flush
        if is_flush:
            return ("Flush", sorted(ranks, reverse=True))

        # Straight
        if is_straight:
            return ("Straight", [straight_high])

        # Three of a Kind
        if counts == [3, 1, 1]:
            three_kind = [r for r, c in rank_counts.items() if c == 3][0]
            kickers = sorted(
                [r for r, c in rank_counts.items() if c == 1], reverse=True
            )
            return ("Three of a Kind", [three_kind] + kickers)

        # Two Pair
        if counts == [2, 2, 1]:
            pairs = sorted([r for r, c in rank_counts.items() if c == 2], reverse=True)
            kicker = [r for r, c in rank_counts.items() if c == 1][0]
            return ("Two Pair", pairs + [kicker])

        # One Pair
        if counts == [2, 1, 1, 1]:
            pair = [r for r, c in rank_counts.items() if c == 2][0]
            kickers = sorted(
                [r for r, c in rank_counts.items() if c == 1], reverse=True
            )
            return ("One Pair", [pair] + kickers)

        # High Card
        return ("High Card", sorted(ranks, reverse=True))

    @staticmethod
    def _check_straight(ranks: List[int]) -> Tuple[bool, int]:
        """Check if cards form a straight. Returns (is_straight, high_card)."""
        sorted_ranks = sorted(set(ranks))

        if len(sorted_ranks) != 5:
            return False, 0

        # Check normal straight
        if sorted_ranks[-1] - sorted_ranks[0] == 4:
            return True, sorted_ranks[-1]

        # Check A-2-3-4-5 (wheel)
        if sorted_ranks == [2, 3, 4, 5, 14]:
            return True, 5  # In wheel, ace is low

        return False, 0

    @staticmethod
    def compare_hands(
        hand1: Tuple[str, List[int]],
        hand2: Tuple[str, List[int]],
        hand1_cards: List[Card] = None,
        hand2_cards: List[Card] = None,
    ) -> int:
        """
        Compare two hands.

        Args:
            hand1: Tuple of (hand_name, kickers) for first hand
            hand2: Tuple of (hand_name, kickers) for second hand
            hand1_cards: Optional list of Card objects for hand1 (for suit tie-breaking)
            hand2_cards: Optional list of Card objects for hand2 (for suit tie-breaking)

        Returns:
            1 if hand1 wins
            -1 if hand2 wins
            0 if tie (after suit comparison if applicable)
        """
        rank1 = HAND_RANKINGS[hand1[0]]
        rank2 = HAND_RANKINGS[hand2[0]]

        if rank1 > rank2:
            return 1
        elif rank1 < rank2:
            return -1
        else:
            # Same hand type, compare kickers
            kickers1 = hand1[1]
            kickers2 = hand2[1]

            for k1, k2 in zip(kickers1, kickers2):
                if k1 > k2:
                    return 1
                elif k1 < k2:
                    return -1

            # Perfect kicker tie - use suit tie-breaking if cards provided
            if hand1_cards and hand2_cards:
                # Compare highest card suits (Spades > Hearts > Diamonds > Clubs)
                # Sort cards by rank descending
                cards1_sorted = sorted(
                    hand1_cards, key=lambda c: RANK_VALUES[c.rank], reverse=True
                )
                cards2_sorted = sorted(
                    hand2_cards, key=lambda c: RANK_VALUES[c.rank], reverse=True
                )

                for c1, c2 in zip(cards1_sorted, cards2_sorted):
                    rank_val1 = RANK_VALUES[c1.rank]
                    rank_val2 = RANK_VALUES[c2.rank]

                    # If same rank, compare suits
                    if rank_val1 == rank_val2:
                        suit_val1 = SUIT_VALUES[c1.suit]
                        suit_val2 = SUIT_VALUES[c2.suit]
                        if suit_val1 > suit_val2:
                            return 1
                        elif suit_val1 < suit_val2:
                            return -1
                        # Same suit and rank, check next card
                    # Different ranks shouldn't happen if kickers matched, but handle it
                    elif rank_val1 > rank_val2:
                        return 1
                    elif rank_val1 < rank_val2:
                        return -1

            return 0  # Perfect tie (even after suit comparison)

    @staticmethod
    def get_best_hand(
        player_cards: List[Card], community_cards: List[Card]
    ) -> Tuple[str, List[int], List[Card]]:
        """
        Get the best hand from player hole cards and community cards.

        Returns:
            Tuple of (hand_name, kickers, best_five_cards)
        """
        all_cards = player_cards + community_cards

        if len(all_cards) < 5:
            raise ValueError("Need at least 5 cards total")

        if len(all_cards) == 5:
            hand_name, kickers = HandEvaluator._evaluate_five_cards(all_cards)
            return hand_name, kickers, all_cards

        # Find best 5-card combination
        from itertools import combinations

        best_hand = ("High Card", [2])
        best_rank = HAND_RANKINGS[best_hand[0]]
        best_cards = all_cards[:5]

        for combo in combinations(all_cards, 5):
            combo_list = list(combo)
            hand_name, kickers = HandEvaluator._evaluate_five_cards(combo_list)
            hand_rank = HAND_RANKINGS[hand_name]

            if hand_rank > best_rank or (
                hand_rank == best_rank and kickers > best_hand[1]
            ):
                best_hand = (hand_name, kickers)
                best_rank = hand_rank
                best_cards = combo_list

        return best_hand[0], best_hand[1], best_cards

    @staticmethod
    def format_hand(hand_name: str, cards: List[Card]) -> str:
        """Format hand for display."""
        card_strs = [f"{c.rank} of {c.suit}" for c in cards]
        return f"{hand_name}: [{', '.join(card_strs)}]"
