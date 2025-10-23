"""
Session Manager for Quantum Poker

Manages temporary player sessions and game tokens without requiring user accounts.
Players get temporary tokens to join games and maintain their session.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Set
from datetime import datetime, timedelta
import secrets
import hashlib


@dataclass
class PlayerSession:
    """Represents a temporary player session."""

    token: str
    username: str
    game_id: Optional[str] = None
    player_number: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)

    def is_expired(self, timeout_minutes: int = 60) -> bool:
        """Check if session has expired."""
        return datetime.now() - self.last_active > timedelta(minutes=timeout_minutes)

    def refresh(self):
        """Update last active timestamp."""
        self.last_active = datetime.now()


@dataclass
class GameSession:
    """Represents a game session with access control."""

    game_id: str
    creator_token: str
    player_tokens: Set[str] = field(default_factory=set)
    max_players: int = 6
    started: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def can_join(self, token: str) -> bool:
        """Check if a player can join this game."""
        return (
            not self.started
            and len(self.player_tokens) < self.max_players
            and token not in self.player_tokens
        )

    def add_player(self, token: str) -> bool:
        """Add a player to the game."""
        if self.can_join(token):
            self.player_tokens.add(token)
            return True
        return False

    def has_player(self, token: str) -> bool:
        """Check if token belongs to a player in this game."""
        return token in self.player_tokens


class SessionManager:
    """Manages player sessions and game access control."""

    def __init__(self, session_timeout_minutes: int = 60):
        self.sessions: Dict[str, PlayerSession] = {}
        self.game_sessions: Dict[str, GameSession] = {}
        self.username_to_token: Dict[str, str] = {}
        self.session_timeout = session_timeout_minutes

    def create_session(self, username: str) -> str:
        """
        Create a new temporary session for a player.

        Args:
            username: Display name for the player

        Returns:
            Session token
        """
        # Generate secure random token
        token = secrets.token_urlsafe(32)

        # Create session
        session = PlayerSession(token=token, username=username)
        self.sessions[token] = session
        self.username_to_token[username] = token

        return token

    def get_session(self, token: str) -> Optional[PlayerSession]:
        """Get session by token."""
        session = self.sessions.get(token)
        if session and not session.is_expired(self.session_timeout):
            session.refresh()
            return session
        elif session:
            # Clean up expired session
            self.remove_session(token)
        return None

    def validate_token(self, token: str) -> bool:
        """Check if token is valid and not expired."""
        return self.get_session(token) is not None

    def remove_session(self, token: str):
        """Remove a session."""
        if token in self.sessions:
            session = self.sessions[token]
            if session.username in self.username_to_token:
                del self.username_to_token[session.username]
            del self.sessions[token]

    def create_game_session(
        self, game_id: str, creator_token: str, max_players: int = 6
    ) -> bool:
        """
        Create a new game session.

        Args:
            game_id: Unique game identifier
            creator_token: Token of the player creating the game
            max_players: Maximum number of players

        Returns:
            True if created successfully
        """
        if not self.validate_token(creator_token):
            return False

        if game_id in self.game_sessions:
            return False

        game_session = GameSession(
            game_id=game_id, creator_token=creator_token, max_players=max_players
        )
        game_session.add_player(creator_token)
        self.game_sessions[game_id] = game_session

        # Update player session
        player_session = self.get_session(creator_token)
        if player_session:
            player_session.game_id = game_id
            player_session.player_number = 1

        return True

    def join_game(self, game_id: str, player_token: str) -> Optional[int]:
        """
        Add a player to a game session.

        Args:
            game_id: Game to join
            player_token: Player's session token

        Returns:
            Player number if successful, None otherwise
        """
        if not self.validate_token(player_token):
            return None

        if game_id not in self.game_sessions:
            return None

        game_session = self.game_sessions[game_id]

        if not game_session.add_player(player_token):
            return None

        # Calculate player number
        player_number = len(game_session.player_tokens)

        # Update player session
        player_session = self.get_session(player_token)
        if player_session:
            player_session.game_id = game_id
            player_session.player_number = player_number

        return player_number

    def verify_game_access(self, game_id: str, player_token: str) -> bool:
        """
        Verify that a player has access to a game.

        Args:
            game_id: Game identifier
            player_token: Player's session token

        Returns:
            True if player has access
        """
        if not self.validate_token(player_token):
            return False

        if game_id not in self.game_sessions:
            return False

        return self.game_sessions[game_id].has_player(player_token)

    def start_game(self, game_id: str, starter_token: str) -> bool:
        """
        Mark a game as started (only creator can start).

        Args:
            game_id: Game identifier
            starter_token: Token of player trying to start

        Returns:
            True if game was started successfully
        """
        if game_id not in self.game_sessions:
            return False

        game_session = self.game_sessions[game_id]

        # Only creator can start
        if game_session.creator_token != starter_token:
            return False

        game_session.started = True
        return True

    def get_game_session(self, game_id: str) -> Optional[GameSession]:
        """Get game session by ID."""
        return self.game_sessions.get(game_id)

    def cleanup_expired_sessions(self):
        """Remove all expired sessions."""
        expired_tokens = [
            token
            for token, session in self.sessions.items()
            if session.is_expired(self.session_timeout)
        ]

        for token in expired_tokens:
            self.remove_session(token)

    def get_active_sessions_count(self) -> int:
        """Get count of active (non-expired) sessions."""
        self.cleanup_expired_sessions()
        return len(self.sessions)

    def get_active_games_count(self) -> int:
        """Get count of active games."""
        return len(self.game_sessions)


# Singleton instance for the application
_session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    return _session_manager
