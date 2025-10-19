import unittest
from src.side_pot_manager import SidePotManager, Pot
from src.card import Card


class TestSidePotManager(unittest.TestCase):
    def test_no_side_pots_equal_bets(self):
        """All players bet the same amount - single main pot"""
        players_bets = {1: (100, False), 2: (100, False), 3: (100, False)}
        
        manager = SidePotManager()
        pots = manager.calculate_pots(players_bets)
        
        self.assertEqual(len(pots), 1)
        self.assertEqual(pots[0].amount, 300)
        self.assertEqual(set(pots[0].eligible_players), {1, 2, 3})
    
    def test_single_all_in(self):
        """One player all-in for less than others"""
        players_bets = {1: (50, True), 2: (100, False), 3: (100, False)}
        
        manager = SidePotManager()
        pots = manager.calculate_pots(players_bets)
        
        self.assertEqual(len(pots), 2)
        # Main pot
        self.assertEqual(pots[0].amount, 150)  # 50 * 3
        self.assertEqual(set(pots[0].eligible_players), {1, 2, 3})
        # Side pot
        self.assertEqual(pots[1].amount, 100)  # (100-50) * 2
        self.assertEqual(set(pots[1].eligible_players), {2, 3})
    
    def test_multiple_all_ins(self):
        """Multiple players all-in for different amounts"""
        players_bets = {1: (50, True), 2: (150, True), 3: (300, False), 4: (300, False)}
        
        manager = SidePotManager()
        pots = manager.calculate_pots(players_bets)
        
        self.assertEqual(len(pots), 3)
        # Main pot: 50 * 4 = 200
        self.assertEqual(pots[0].amount, 200)
        self.assertEqual(set(pots[0].eligible_players), {1, 2, 3, 4})
        # Side pot 1: (150-50) * 3 = 300
        self.assertEqual(pots[1].amount, 300)
        self.assertEqual(set(pots[1].eligible_players), {2, 3, 4})
        # Side pot 2: (300-150) * 2 = 300
        self.assertEqual(pots[2].amount, 300)
        self.assertEqual(set(pots[2].eligible_players), {3, 4})
    
    def test_all_players_all_in_equal(self):
        """All players all-in for the same amount"""
        players_bets = {1: (100, True), 2: (100, True), 3: (100, True)}
        
        manager = SidePotManager()
        pots = manager.calculate_pots(players_bets)
        
        self.assertEqual(len(pots), 1)
        self.assertEqual(pots[0].amount, 300)
        self.assertEqual(set(pots[0].eligible_players), {1, 2, 3})
    
    def test_all_players_all_in_different(self):
        """All players all-in for different amounts"""
        players_bets = {1: (50, True), 2: (100, True), 3: (150, True)}
        
        manager = SidePotManager()
        pots = manager.calculate_pots(players_bets)
        
        self.assertEqual(len(pots), 3)
        # Main pot: 50 * 3 = 150
        self.assertEqual(pots[0].amount, 150)
        self.assertEqual(set(pots[0].eligible_players), {1, 2, 3})
        # Side pot 1: (100-50) * 2 = 100
        self.assertEqual(pots[1].amount, 100)
        self.assertEqual(set(pots[1].eligible_players), {2, 3})
        # Side pot 2: (150-100) * 1 = 50
        self.assertEqual(pots[2].amount, 50)
        self.assertEqual(set(pots[2].eligible_players), {3})
    
    def test_player_folds_not_in_pots(self):
        """Folded player not eligible for any pots"""
        # Player 3 has 0 bet (folded), so they should not be in any pot
        players_bets = {1: (50, True), 2: (100, False)}
        
        manager = SidePotManager()
        pots = manager.calculate_pots(players_bets)
        
        # Check no pot includes player 3
        for pot in pots:
            self.assertNotIn(3, pot.eligible_players)
    
    def test_award_single_pot_single_winner(self):
        """Award single pot to single winner"""
        # Setup pots
        manager = SidePotManager()
        manager.pots = [Pot(amount=300, eligible_players=[1, 2, 3])]
        
        # Player 1 has Royal Flush, others have High Card
        player_hands = {
            1: ('Royal Flush', [14, 13, 12, 11, 10]),
            2: ('High Card', [14, 12, 10, 8, 6]),
            3: ('High Card', [13, 11, 9, 7, 5])
        }
        
        awards = manager.award_pots(player_hands)
        
        self.assertEqual(awards[1], 300)
        self.assertEqual(awards[2], 0)
        self.assertEqual(awards[3], 0)
    
    def test_award_single_pot_split(self):
        """Split pot between tied winners"""
        manager = SidePotManager()
        manager.pots = [Pot(amount=300, eligible_players=[1, 2, 3])]
        
        # Players 1 and 2 have identical hands
        player_hands = {
            1: ('One Pair', [14, 14, 12, 10, 8]),
            2: ('One Pair', [14, 14, 12, 10, 8]),
            3: ('High Card', [13, 11, 9, 7, 5])
        }
        
        awards = manager.award_pots(player_hands)
        
        self.assertEqual(awards[1], 150)
        self.assertEqual(awards[2], 150)
        self.assertEqual(awards[3], 0)
    
    def test_award_multiple_pots_different_winners(self):
        """Different winners for main and side pots"""
        manager = SidePotManager()
        manager.pots = [
            Pot(amount=150, eligible_players=[1, 2, 3]),
            Pot(amount=100, eligible_players=[2, 3])
        ]
        
        # P1 has best hand overall but only eligible for main pot
        # P3 has second best hand, wins side pot
        player_hands = {
            1: ('Full House', [14, 14, 14, 13, 13]),
            2: ('Two Pair', [14, 14, 13, 13, 12]),
            3: ('Three of a Kind', [12, 12, 12, 11, 9])
        }
        
        awards = manager.award_pots(player_hands)
        
        self.assertEqual(awards[1], 150)  # Wins main pot
        self.assertEqual(awards[2], 0)    # Loses both pots
        self.assertEqual(awards[3], 100)  # Wins side pot
    
    def test_award_split_with_remainder(self):
        """Split pot with odd amount - remainder is lost"""
        manager = SidePotManager()
        manager.pots = [Pot(amount=101, eligible_players=[1, 2])]
        
        # Both players have identical hands
        player_hands = {
            1: ('Flush', [14, 12, 10, 8, 6]),
            2: ('Flush', [14, 12, 10, 8, 6])
        }
        
        awards = manager.award_pots(player_hands)
        
        # 101 // 2 = 50 each (1 chip remainder is lost due to integer division)
        self.assertEqual(awards[1], 50)
        self.assertEqual(awards[2], 50)
    
    def test_get_pot_display(self):
        """Test pot display formatting"""
        manager = SidePotManager()
        manager.pots = [
            Pot(amount=150, eligible_players=[1, 2, 3]),
            Pot(amount=100, eligible_players=[2, 3])
        ]
        
        display = manager.get_pot_display()
        
        self.assertEqual(len(display), 2)
        self.assertIn("Main Pot", display[0])
        self.assertIn("150", display[0])
        self.assertIn("Side Pot 1", display[1])
        self.assertIn("100", display[1])


if __name__ == '__main__':
    unittest.main()
