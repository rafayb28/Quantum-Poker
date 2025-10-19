import unittest
from datetime import datetime, timedelta
from src.session_manager import SessionManager, PlayerSession, GameSession


class TestSessionManager(unittest.TestCase):
    def setUp(self):
        """Create a fresh session manager for each test."""
        self.manager = SessionManager(session_timeout_minutes=60)
    
    def test_create_session(self):
        """Test creating a new player session."""
        token = self.manager.create_session("Alice")
        
        self.assertIsNotNone(token)
        self.assertIn(token, self.manager.sessions)
        
        session = self.manager.get_session(token)
        self.assertIsNotNone(session)
        self.assertEqual(session.username, "Alice")
        self.assertIsNone(session.game_id)
    
    def test_validate_token(self):
        """Test token validation."""
        token = self.manager.create_session("Bob")
        
        # Valid token
        self.assertTrue(self.manager.validate_token(token))
        
        # Invalid token
        self.assertFalse(self.manager.validate_token("invalid_token"))
    
    def test_session_refresh(self):
        """Test that accessing a session refreshes it."""
        token = self.manager.create_session("Charlie")
        
        session1 = self.manager.get_session(token)
        first_access = session1.last_active
        
        # Small delay
        import time
        time.sleep(0.1)
        
        session2 = self.manager.get_session(token)
        second_access = session2.last_active
        
        self.assertGreater(second_access, first_access)
    
    def test_session_expiration(self):
        """Test session expiration."""
        # Create session with 1 minute timeout
        manager = SessionManager(session_timeout_minutes=0)
        token = manager.create_session("Dave")
        
        # Manually set last_active to past
        session = manager.sessions[token]
        session.last_active = datetime.now() - timedelta(minutes=2)
        
        # Should be expired
        self.assertTrue(session.is_expired(timeout_minutes=1))
        
        # Get session should return None and clean up
        self.assertIsNone(manager.get_session(token))
        self.assertNotIn(token, manager.sessions)
    
    def test_create_game_session(self):
        """Test creating a game session."""
        token = self.manager.create_session("Eve")
        game_id = "game123"
        
        success = self.manager.create_game_session(game_id, token, max_players=4)
        
        self.assertTrue(success)
        self.assertIn(game_id, self.manager.game_sessions)
        
        game_session = self.manager.get_game_session(game_id)
        self.assertEqual(game_session.game_id, game_id)
        self.assertEqual(game_session.creator_token, token)
        self.assertIn(token, game_session.player_tokens)
        
        # Check player session updated
        player_session = self.manager.get_session(token)
        self.assertEqual(player_session.game_id, game_id)
        self.assertEqual(player_session.player_number, 1)
    
    def test_join_game(self):
        """Test joining an existing game."""
        creator_token = self.manager.create_session("Frank")
        joiner_token = self.manager.create_session("Grace")
        game_id = "game456"
        
        # Create game
        self.manager.create_game_session(game_id, creator_token)
        
        # Join game
        player_number = self.manager.join_game(game_id, joiner_token)
        
        self.assertIsNotNone(player_number)
        self.assertEqual(player_number, 2)
        
        # Verify access
        self.assertTrue(self.manager.verify_game_access(game_id, joiner_token))
        
        # Check player session
        session = self.manager.get_session(joiner_token)
        self.assertEqual(session.game_id, game_id)
        self.assertEqual(session.player_number, 2)
    
    def test_join_full_game(self):
        """Test that players can't join a full game."""
        game_id = "game789"
        creator_token = self.manager.create_session("Host")
        
        # Create game with max 2 players
        self.manager.create_game_session(game_id, creator_token, max_players=2)
        
        # First player can join
        player1_token = self.manager.create_session("Player1")
        result1 = self.manager.join_game(game_id, player1_token)
        self.assertIsNotNone(result1)
        
        # Second player cannot join (game full)
        player2_token = self.manager.create_session("Player2")
        result2 = self.manager.join_game(game_id, player2_token)
        self.assertIsNone(result2)
    
    def test_join_nonexistent_game(self):
        """Test joining a game that doesn't exist."""
        token = self.manager.create_session("Hannah")
        result = self.manager.join_game("nonexistent", token)
        
        self.assertIsNone(result)
    
    def test_verify_game_access(self):
        """Test game access verification."""
        creator_token = self.manager.create_session("Ian")
        unauthorized_token = self.manager.create_session("Intruder")
        game_id = "secure_game"
        
        self.manager.create_game_session(game_id, creator_token)
        
        # Creator has access
        self.assertTrue(self.manager.verify_game_access(game_id, creator_token))
        
        # Unauthorized player does not
        self.assertFalse(self.manager.verify_game_access(game_id, unauthorized_token))
    
    def test_start_game(self):
        """Test starting a game."""
        creator_token = self.manager.create_session("Jack")
        other_token = self.manager.create_session("Jill")
        game_id = "start_test"
        
        self.manager.create_game_session(game_id, creator_token)
        self.manager.join_game(game_id, other_token)
        
        # Creator can start
        result = self.manager.start_game(game_id, creator_token)
        self.assertTrue(result)
        
        game_session = self.manager.get_game_session(game_id)
        self.assertTrue(game_session.started)
    
    def test_non_creator_cannot_start(self):
        """Test that only creator can start a game."""
        creator_token = self.manager.create_session("Kevin")
        other_token = self.manager.create_session("Laura")
        game_id = "creator_only"
        
        self.manager.create_game_session(game_id, creator_token)
        self.manager.join_game(game_id, other_token)
        
        # Non-creator cannot start
        result = self.manager.start_game(game_id, other_token)
        self.assertFalse(result)
        
        game_session = self.manager.get_game_session(game_id)
        self.assertFalse(game_session.started)
    
    def test_cannot_join_started_game(self):
        """Test that players can't join a game that's already started."""
        creator_token = self.manager.create_session("Mike")
        late_token = self.manager.create_session("Nancy")
        game_id = "already_started"
        
        self.manager.create_game_session(game_id, creator_token)
        self.manager.start_game(game_id, creator_token)
        
        # Late player cannot join
        result = self.manager.join_game(game_id, late_token)
        self.assertIsNone(result)
    
    def test_cleanup_expired_sessions(self):
        """Test cleaning up expired sessions."""
        manager = SessionManager(session_timeout_minutes=1)
        
        token1 = manager.create_session("Oliver")
        token2 = manager.create_session("Patricia")
        
        # Manually expire one session
        manager.sessions[token1].last_active = datetime.now() - timedelta(minutes=2)
        
        manager.cleanup_expired_sessions()
        
        # Expired session removed
        self.assertNotIn(token1, manager.sessions)
        # Active session remains
        self.assertIn(token2, manager.sessions)
    
    def test_active_counts(self):
        """Test getting active session and game counts."""
        token1 = self.manager.create_session("Quinn")
        token2 = self.manager.create_session("Rachel")
        
        self.assertEqual(self.manager.get_active_sessions_count(), 2)
        
        self.manager.create_game_session("game1", token1)
        self.assertEqual(self.manager.get_active_games_count(), 1)
    
    def test_remove_session(self):
        """Test manually removing a session."""
        token = self.manager.create_session("Sam")
        
        self.assertIn(token, self.manager.sessions)
        
        self.manager.remove_session(token)
        
        self.assertNotIn(token, self.manager.sessions)
        self.assertFalse(self.manager.validate_token(token))
    
    def test_duplicate_username(self):
        """Test that same username gets new token."""
        token1 = self.manager.create_session("Taylor")
        token2 = self.manager.create_session("Taylor")
        
        # Different tokens
        self.assertNotEqual(token1, token2)
        
        # Latest token is in username mapping
        self.assertEqual(self.manager.username_to_token["Taylor"], token2)


if __name__ == '__main__':
    unittest.main()
