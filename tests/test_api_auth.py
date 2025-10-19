"""
Integration tests for API authentication.
Tests the session-based auth flow end-to-end.
"""

import pytest
from fastapi.testclient import TestClient
from src.api import app, session_manager


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up sessions between tests."""
    yield
    session_manager.sessions.clear()
    session_manager.game_sessions.clear()
    session_manager.username_to_token.clear()


class TestAuthentication:
    """Test authentication and session management."""
    
    def test_create_session(self, client):
        """Test creating a new session."""
        response = client.post(
            "/auth/session",
            json={"username": "Alice"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "token" in data
        assert data["username"] == "Alice"
        assert "message" in data
        assert len(data["token"]) > 20  # Secure token
    
    def test_validate_session(self, client):
        """Test validating a session token."""
        # Create session
        create_resp = client.post(
            "/auth/session",
            json={"username": "Bob"}
        )
        token = create_resp.json()["token"]
        
        # Validate
        response = client.get(
            "/auth/validate",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["username"] == "Bob"
    
    def test_invalid_token(self, client):
        """Test that invalid token is rejected."""
        response = client.get(
            "/auth/validate",
            headers={"Authorization": "Bearer invalid_token_123"}
        )
        
        assert response.status_code == 401
    
    def test_missing_auth_header(self, client):
        """Test that missing auth header is rejected."""
        response = client.get("/auth/validate")
        
        assert response.status_code == 401


class TestGameCreation:
    """Test game creation with authentication."""
    
    def test_create_game_with_auth(self, client):
        """Test creating a game with valid auth."""
        # Create session
        session_resp = client.post(
            "/auth/session",
            json={"username": "Charlie"}
        )
        token = session_resp.json()["token"]
        
        # Create game
        response = client.post(
            "/game/create",
            json={"num_players": 2, "max_players": 4},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "game_id" in data
        assert data["player_number"] == 1
        assert "message" in data
    
    def test_create_game_without_auth(self, client):
        """Test that creating game without auth fails."""
        response = client.post(
            "/game/create",
            json={"num_players": 2}
        )
        
        assert response.status_code == 401
    
    def test_join_game_with_auth(self, client):
        """Test joining a game with valid auth."""
        # Player 1 creates session and game
        p1_resp = client.post("/auth/session", json={"username": "Dave"})
        p1_token = p1_resp.json()["token"]
        
        game_resp = client.post(
            "/game/create",
            json={"num_players": 2},
            headers={"Authorization": f"Bearer {p1_token}"}
        )
        game_id = game_resp.json()["game_id"]
        
        # Player 2 creates session and joins
        p2_resp = client.post("/auth/session", json={"username": "Eve"})
        p2_token = p2_resp.json()["token"]
        
        join_resp = client.post(
            f"/game/{game_id}/join",
            headers={"Authorization": f"Bearer {p2_token}"}
        )
        
        assert join_resp.status_code == 200
        data = join_resp.json()
        assert data["player_number"] == 2
        assert "Eve" in data["message"]
    
    def test_join_nonexistent_game(self, client):
        """Test joining a game that doesn't exist."""
        session_resp = client.post("/auth/session", json={"username": "Frank"})
        token = session_resp.json()["token"]
        
        response = client.post(
            "/game/nonexistent123/join",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404


class TestGameAccess:
    """Test game access control."""
    
    def test_unauthorized_cannot_view_game(self, client):
        """Test that unauthorized players cannot view game state."""
        # Create game
        p1_resp = client.post("/auth/session", json={"username": "Grace"})
        p1_token = p1_resp.json()["token"]
        
        game_resp = client.post(
            "/game/create",
            json={"num_players": 2},
            headers={"Authorization": f"Bearer {p1_token}"}
        )
        game_id = game_resp.json()["game_id"]
        
        # Unauthorized player tries to view
        p2_resp = client.post("/auth/session", json={"username": "Hacker"})
        p2_token = p2_resp.json()["token"]
        
        response = client.get(
            f"/game/{game_id}/state",
            headers={"Authorization": f"Bearer {p2_token}"}
        )
        
        assert response.status_code == 403
    
    def test_only_creator_can_start(self, client):
        """Test that only game creator can start the game."""
        # Create game
        p1_resp = client.post("/auth/session", json={"username": "Ian"})
        p1_token = p1_resp.json()["token"]
        
        game_resp = client.post(
            "/game/create",
            json={"num_players": 2},
            headers={"Authorization": f"Bearer {p1_token}"}
        )
        game_id = game_resp.json()["game_id"]
        
        # Player 2 joins
        p2_resp = client.post("/auth/session", json={"username": "Jane"})
        p2_token = p2_resp.json()["token"]
        
        client.post(
            f"/game/{game_id}/join",
            headers={"Authorization": f"Bearer {p2_token}"}
        )
        
        # Player 2 tries to start (should fail)
        start_resp = client.post(
            f"/game/{game_id}/start",
            headers={"Authorization": f"Bearer {p2_token}"}
        )
        
        assert start_resp.status_code == 403
        
        # Player 1 can start (should succeed)
        start_resp = client.post(
            f"/game/{game_id}/start",
            headers={"Authorization": f"Bearer {p1_token}"}
        )
        
        assert start_resp.status_code == 200


class TestStats:
    """Test stats endpoints."""
    
    def test_health_check_public(self, client):
        """Test that health check is public."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_stats_requires_auth(self, client):
        """Test that stats endpoint requires auth."""
        response = client.get("/stats")
        
        assert response.status_code == 401
    
    def test_stats_with_auth(self, client):
        """Test getting stats with valid auth."""
        session_resp = client.post("/auth/session", json={"username": "Kevin"})
        token = session_resp.json()["token"]
        
        response = client.get(
            "/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "active_sessions" in data
        assert "active_games" in data
        assert "games" in data
    
    def test_list_games(self, client):
        """Test listing available games."""
        # Create session
        session_resp = client.post("/auth/session", json={"username": "Laura"})
        token = session_resp.json()["token"]
        
        # Create game
        client.post(
            "/game/create",
            json={"num_players": 2},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # List games
        response = client.get(
            "/games/list",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "games" in data
        assert len(data["games"]) >= 1


if __name__ == '__main__':
    pytest.main([__file__, "-v"])
