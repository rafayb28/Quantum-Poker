# Authentication & Session Management

## Overview

Quantum Poker uses a **lightweight token-based authentication system** designed for casual gameplay without requiring user registration. Players create temporary sessions with display names and receive secure tokens to access games.

## Key Features

- 🎭 **No registration required** - Just pick a username
- 🔐 **Secure tokens** - Cryptographically random 32-byte tokens
- ⏱️ **Automatic expiration** - Sessions expire after 60 minutes of inactivity
- 🎮 **Game-level access control** - Only players in a game can view/modify it
- 👥 **Multi-player support** - Up to 6 players per game (configurable)
- 🚀 **Stateless design** - Ready for Redis/database in production

## Authentication Flow

### 1. Create Session

```bash
POST /auth/session
Content-Type: application/json

{
  "username": "Alice"
}
```

**Response:**
```json
{
  "token": "vK8x3nM2pL9q...",
  "username": "Alice",
  "message": "Session created for Alice"
}
```

### 2. Use Token in Requests

All protected endpoints require the token in the `Authorization` header:

```bash
Authorization: Bearer vK8x3nM2pL9q...
```

### 3. Validate Token

```bash
GET /auth/validate
Authorization: Bearer vK8x3nM2pL9q...
```

**Response:**
```json
{
  "valid": true,
  "username": "Alice",
  "game_id": "abc123",
  "player_number": 1
}
```

## Game Access Control

### Creating a Game

```bash
POST /game/create
Authorization: Bearer <token>
Content-Type: application/json

{
  "num_players": 2,
  "max_players": 6
}
```

- Creator becomes **Player 1**
- Creator is the only one who can **start the game**
- Game ID and session are linked

### Joining a Game

```bash
POST /game/{game_id}/join
Authorization: Bearer <token>
```

**Rules:**
- Cannot join if game is full
- Cannot join if game already started
- Each player gets a unique player number
- Player's token grants access to game state

### Game Permissions

| Action | Who Can Do It |
|--------|---------------|
| Create game | Any authenticated user |
| Join game | Any authenticated user (if space available) |
| Start game | **Creator only** |
| View game state | Players in the game only |
| Make moves | Players in the game only |
| View circuit | Players in the game only |

## Protected Endpoints

### Requires Authentication (Any Valid Token)

- `POST /game/create` - Create a new game
- `GET /games/list` - List available games
- `GET /stats` - Get server statistics

### Requires Game Access (Must be in the game)

- `GET /game/{game_id}/state` - View game state
- `POST /game/{game_id}/join` - Join a game
- `POST /game/{game_id}/action` - Make a move
- `POST /game/{game_id}/quantum-action` - Perform quantum action
- `GET /game/{game_id}/circuit` - View quantum circuit
- `POST /game/{game_id}/showdown` - Trigger showdown
- `POST /game/{game_id}/next-round` - Advance to next round

### Requires Creator Permissions

- `POST /game/{game_id}/start` - Start the game

## Session Management

### Session Data

Each session stores:
- **Token**: Secure random identifier
- **Username**: Display name
- **Game ID**: Current game (if joined)
- **Player Number**: Position in game (1-6)
- **Created At**: Session creation time
- **Last Active**: Last activity timestamp

### Session Expiration

- Sessions expire after **60 minutes** of inactivity
- Any API call refreshes the session
- Expired sessions are automatically cleaned up
- No manual logout required

### Game Sessions

Each game session tracks:
- **Game ID**: Unique identifier
- **Creator Token**: Who created the game
- **Player Tokens**: All players in the game
- **Max Players**: Maximum allowed (default 6)
- **Started**: Whether game has begun

## Error Responses

### 401 Unauthorized

```json
{
  "detail": "Missing authorization header"
}
```

Causes:
- No `Authorization` header
- Invalid token format
- Expired token

### 403 Forbidden

```json
{
  "detail": "Access denied to this game"
}
```

Causes:
- Token valid but not in this game
- Non-creator trying to start game

### 404 Not Found

```json
{
  "detail": "Game not found"
}
```

## Example Usage

### Complete Flow

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Player 1 creates session
resp = requests.post(f"{BASE_URL}/auth/session", json={"username": "Alice"})
alice_token = resp.json()["token"]
headers_alice = {"Authorization": f"Bearer {alice_token}"}

# 2. Player 1 creates game
resp = requests.post(
    f"{BASE_URL}/game/create",
    json={"num_players": 2},
    headers=headers_alice
)
game_id = resp.json()["game_id"]

# 3. Player 2 creates session
resp = requests.post(f"{BASE_URL}/auth/session", json={"username": "Bob"})
bob_token = resp.json()["token"]
headers_bob = {"Authorization": f"Bearer {bob_token}"}

# 4. Player 2 joins game
resp = requests.post(
    f"{BASE_URL}/game/{game_id}/join",
    headers=headers_bob
)

# 5. Player 1 starts game
resp = requests.post(
    f"{BASE_URL}/game/{game_id}/start",
    headers=headers_alice
)

# 6. Both players can view game state
resp = requests.get(
    f"{BASE_URL}/game/{game_id}/state",
    headers=headers_alice
)
game_state = resp.json()
```

## Security Considerations

### Current Implementation (Development)

- In-memory session storage
- Tokens are cryptographically secure (32 bytes)
- No password or personal data required
- Sessions auto-expire

### Production Recommendations

1. **Use Redis** for session storage (horizontal scaling)
2. **Add rate limiting** to prevent abuse
3. **Enable HTTPS** for encrypted token transmission
4. **Add CORS** whitelist for specific frontend domains
5. **Implement refresh tokens** for long-running games
6. **Add WebSocket authentication** for real-time updates
7. **Log authentication attempts** for security monitoring

## Admin Endpoints

### Health Check (Public)

```bash
GET /health
```

Returns:
- Server status
- Active sessions count
- Active games count

### Stats (Requires Auth)

```bash
GET /stats
Authorization: Bearer <token>
```

Returns detailed server statistics including game list.

## Future Enhancements

- [ ] Optional user accounts for persistent history
- [ ] OAuth integration (Google, GitHub)
- [ ] Session persistence across server restarts
- [ ] IP-based rate limiting
- [ ] Token refresh mechanism
- [ ] Admin dashboard tokens
- [ ] Spectator tokens (view-only access)
