"""
FastAPI Backend for Quantum Poker

To run: uvicorn src.api:app --reload
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
import uuid

from .game import QuantumPoker
from .session_manager import get_session_manager, SessionManager

app = FastAPI(title="Quantum Poker API", version="0.1.0")

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory game storage (use Redis/DB in production)
active_games: Dict[str, QuantumPoker] = {}
game_players: Dict[str, Dict[int, str]] = {}  # game_id -> {player_number: player_name}

# Session manager
session_manager = get_session_manager()

# Security
security = HTTPBearer()

# ============================================================================
# Authentication Dependencies
# ============================================================================


async def verify_token(authorization: Optional[str] = Header(None)) -> str:
    """
    Verify session token from Authorization header.
    
    Expected format: "Bearer <token>"
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization.replace("Bearer ", "")
    
    if not session_manager.validate_token(token):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return token


async def verify_game_access(game_id: str, token: str = Depends(verify_token)) -> str:
    """
    Verify that the authenticated player has access to the specified game.
    """
    if not session_manager.verify_game_access(game_id, token):
        raise HTTPException(status_code=403, detail="Access denied to this game")
    
    return token


# ============================================================================
# Data Models (Pydantic schemas for API)
# ============================================================================


class ActionType(str, Enum):
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    RAISE = "raise"
    ALL_IN = "all_in"


class QuantumActionType(str, Enum):
    ENTANGLE = "entangle"
    # Future: SUPERPOSITION, TELEPORT, etc.


class CreateSessionRequest(BaseModel):
    username: str


class CreateSessionResponse(BaseModel):
    token: str
    username: str
    message: str


class CreateGameRequest(BaseModel):
    num_players: int = 2
    max_players: int = 6


class CreateGameResponse(BaseModel):
    game_id: str
    player_number: int
    message: str


class JoinGameResponse(BaseModel):
    game_id: str
    player_number: int
    message: str


class PlayerActionRequest(BaseModel):
    action: ActionType
    amount: Optional[int] = None  # For raise/bet


class QuantumActionRequest(BaseModel):
    action: QuantumActionType
    source_card_idx: int  # 0 or 1 for hole cards
    target_card_id: str  # e.g., "F0", "P2H1"
    bit_index: int  # 0-2 (rank bits only: 0=±1, 1=±2, 2=±4)


class PlayerState(BaseModel):
    name: str
    number: int
    chips: int
    quantum_chips: int
    current_bet: int
    folded: bool
    hand_identifiers: List[str]


class GameState(BaseModel):
    game_id: str
    round: str
    pot: int
    current_bet: int
    players: List[PlayerState]
    community_cards: Dict[str, Any]
    entanglements: Dict[str, List[Tuple]]
    current_player: Optional[int]


# ============================================================================
# In-memory storage (Replace with Redis/Database in production)
# ============================================================================

games: Dict[str, any] = {}  # game_id -> QuantumPoker instance
websocket_connections: Dict[str, List[WebSocket]] = {}  # game_id -> [websockets]


# ============================================================================
# API Endpoints
# ============================================================================


@app.get("/")
async def root():
    return {
        "message": "Quantum Poker API",
        "version": "0.2.0",
        "status": "operational",
        "auth": "token-based"
    }


@app.post("/auth/session", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest):
    """
    Create a new temporary session for a player.
    No registration required - just pick a username.
    """
    token = session_manager.create_session(request.username)
    
    return CreateSessionResponse(
        token=token,
        username=request.username,
        message=f"Session created for {request.username}"
    )


@app.get("/auth/validate")
async def validate_session(token: str = Depends(verify_token)):
    """
    Validate if a token is still valid.
    """
    session = session_manager.get_session(token)
    return {
        "valid": True,
        "username": session.username,
        "game_id": session.game_id,
        "player_number": session.player_number
    }


@app.post("/game/create", response_model=CreateGameResponse)
async def create_game(
    request: CreateGameRequest,
    token: str = Depends(verify_token)
):
    """
    Create a new quantum poker game.
    Requires authentication token.
    """
    game_id = str(uuid.uuid4())
    
    # Create game session
    if not session_manager.create_game_session(
        game_id, 
        token, 
        max_players=request.max_players
    ):
        raise HTTPException(status_code=400, detail="Failed to create game session")
    
    # Initialize QuantumPoker instance
    game = QuantumPoker(num_players=request.num_players)
    active_games[game_id] = game
    
    # Get creator info
    session = session_manager.get_session(token)
    game_players[game_id] = {1: session.username}
    game.players[0].name = session.username

    return CreateGameResponse(
        game_id=game_id,
        player_number=1,
        message="Game created successfully"
    )


@app.post("/game/{game_id}/join", response_model=JoinGameResponse)
async def join_game(
    game_id: str,
    token: str = Depends(verify_token)
):
    """
    Join an existing game.
    Requires authentication token.
    """
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")

    # Join game session
    player_number = session_manager.join_game(game_id, token)
    if player_number is None:
        raise HTTPException(
            status_code=400,
            detail="Cannot join game (full or already started)"
        )
    
    # Update game instance
    game = active_games[game_id]
    session = session_manager.get_session(token)
    game_players[game_id][player_number] = session.username
    game.players[player_number - 1].name = session.username

    return JoinGameResponse(
        game_id=game_id,
        player_number=player_number,
        message=f"{session.username} joined game"
    )


@app.post("/game/{game_id}/start")
async def start_game(
    game_id: str,
    token: str = Depends(verify_game_access)
):
    """
    Start the game (deal initial cards, post blinds).
    Only the game creator can start the game.
    """
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Verify creator
    if not session_manager.start_game(game_id, token):
        raise HTTPException(
            status_code=403,
            detail="Only game creator can start the game"
        )
    
    game = active_games[game_id]
    
    if len(game_players[game_id]) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 players to start")
    
    # Start the game (deals cards, posts blinds, transitions to pre-flop)
    try:
        game.start_game()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {
        "message": "Game started",
        "state": game.to_dict()
    }


@app.get("/game/{game_id}/state")
async def get_game_state(
    game_id: str,
    token: str = Depends(verify_game_access)
):
    """
    Get current state of the game.
    Only players in the game can view the state.
    """
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")

    game = active_games[game_id]
    session = session_manager.get_session(token)
    
    # Get game state and add actual player count
    state = game.to_dict(viewing_player=session.player_number)
    state['players_joined'] = len(game_players.get(game_id, {}))
    
    return state


@app.post("/game/{game_id}/action")
async def perform_action(
    game_id: str,
    request: PlayerActionRequest,
    token: str = Depends(verify_game_access)
):
    """
    Perform a standard poker action (fold, check, call, raise).
    Token authentication determines which player is acting.
    """
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")

    game = active_games[game_id]
    session = session_manager.get_session(token)
    player_number = session.player_number
    
    if player_number < 1 or player_number > game.num_players:
        raise HTTPException(status_code=400, detail="Invalid player number")
    
    player = game.players[player_number - 1]
    
    if game.current_player_idx != player_number - 1:
        raise HTTPException(status_code=400, detail="Not your turn")
    
    # Process action
    try:
        action_type = request.action.value
        amount_to_call = game.current_bet - player.current_bet
        
        if action_type == "fold":
            player.fold()
            result = {"action": "fold"}
            
        elif action_type == "check":
            if amount_to_call > 0:
                raise HTTPException(status_code=400, detail="Cannot check, must call or fold")
            result = {"action": "check"}
            
        elif action_type == "call":
            actual_bet = player.call(amount_to_call)
            game.pot += actual_bet
            result = {"action": "call", "amount": actual_bet}
            
        elif action_type == "raise":
            if not request.amount:
                raise HTTPException(status_code=400, detail="Raise amount required")
            actual_bet = player.raise_bet(game.current_bet, request.amount)
            game.pot += actual_bet
            game.current_bet = player.current_bet
            result = {"action": "raise", "amount": actual_bet, "new_bet": game.current_bet}
            
        elif action_type == "all_in":
            actual_bet = player.bet(player.chips)
            game.pot += actual_bet
            if player.current_bet > game.current_bet:
                game.current_bet = player.current_bet
            result = {"action": "all_in", "amount": actual_bet}
        
        # Move to next player
        game.current_player_idx = (game.current_player_idx + 1) % game.num_players
        
        return {
            "message": f"Action {action_type} performed",
            "result": result,
            "state": game.to_dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/game/{game_id}/quantum-action")
async def perform_quantum_action(
    game_id: str,
    request: QuantumActionRequest,
    token: str = Depends(verify_game_access)
):
    """
    Perform a quantum action (entanglement, etc.).
    Token authentication determines which player is acting.
    """
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")

    game = active_games[game_id]
    session = session_manager.get_session(token)
    player_number = session.player_number
    
    if player_number < 1 or player_number > game.num_players:
        raise HTTPException(status_code=400, detail="Invalid player number")
    
    player = game.players[player_number - 1]
    
    try:
        if request.action == QuantumActionType.ENTANGLE:
            # Validate quantum chips
            if player.quantum_chips <= 0:
                raise HTTPException(status_code=400, detail="No quantum chips remaining")
            
            # Validate bit index (only rank bits 0-2 allowed)
            if request.bit_index < 0 or request.bit_index > 2:
                raise HTTPException(status_code=400, detail="Invalid bit index. Only rank bits 0-2 allowed")
            
            # Perform entanglement
            source_id = f"P{player_number}H{request.source_card_idx + 1}"
            game.qc_manager.entangle_cards(source_id, request.target_card_id, request.bit_index)
            player.use_quantum_chip()
            
            bit_effects = ["±1", "±2", "±4"]
            
            return {
                "message": "Quantum entanglement successful",
                "source": source_id,
                "target": request.target_card_id,
                "bit": request.bit_index,
                "effect": bit_effects[request.bit_index],
                "quantum_chips_remaining": player.quantum_chips,
                "state": game.to_dict(viewing_player=player_number)
            }
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/game/{game_id}/circuit")
async def get_circuit_diagram(
    game_id: str,
    token: str = Depends(verify_game_access)
):
    """
    Get the quantum circuit diagram as text.
    Only players in the game can view the circuit.
    """
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")

    game = active_games[game_id]
    circuit_diagram = game.get_circuit_diagram()

    return {"circuit": circuit_diagram}


@app.post("/game/{game_id}/showdown")
async def trigger_showdown(
    game_id: str,
    token: str = Depends(verify_game_access)
):
    """
    Trigger showdown (measure all cards).
    Any player in the game can trigger showdown.
    """
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")

    game = active_games[game_id]
    
    try:
        showdown_results = game.showdown()
        
        return {
            "message": "Showdown complete",
            "results": showdown_results,
            "state": game.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Showdown failed: {str(e)}")


@app.post("/game/{game_id}/next-round")
async def advance_round(
    game_id: str,
    token: str = Depends(verify_game_access)
):
    """
    Advance to the next round (flop, turn, river).
    Any player in the game can advance rounds.
    """
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")

    game = active_games[game_id]
    
    try:
        if game.current_round == "pre-flop":
            game.deal_flop()
            return {"message": "Flop dealt", "state": game.to_dict()}
            
        elif game.current_round == "flop":
            game.deal_turn()
            return {"message": "Turn dealt", "state": game.to_dict()}
            
        elif game.current_round == "turn":
            game.deal_river()
            return {"message": "River dealt", "state": game.to_dict()}
            
        elif game.current_round == "river":
            return {"message": "Already at river, trigger showdown", "state": game.to_dict()}
            
        else:
            raise HTTPException(status_code=400, detail="Invalid game state")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



# ============================================================================
# WebSocket for Real-time Updates
# ============================================================================

websocket_connections: Dict[str, List[WebSocket]] = {}


async def broadcast_game_state(game_id: str):
    """Broadcast game state to all connected clients."""
    if game_id not in active_games or game_id not in websocket_connections:
        return
    
    game = active_games[game_id]
    state = game.to_dict()
    
    disconnected = []
    for websocket in websocket_connections[game_id]:
        try:
            await websocket.send_json({
                "type": "game_update",
                "state": state
            })
        except:
            disconnected.append(websocket)
    
    # Remove disconnected clients
    for ws in disconnected:
        websocket_connections[game_id].remove(ws)


@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    """
    WebSocket connection for real-time game updates.
    """
    await websocket.accept()

    # Add to connections
    if game_id not in websocket_connections:
        websocket_connections[game_id] = []
    websocket_connections[game_id].append(websocket)

    try:
        # Send initial game state
        if game_id in active_games:
            game = active_games[game_id]
            await websocket.send_json({
                "type": "connected",
                "state": game.to_dict()
            })
        
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            
            # Echo acknowledgment
            await websocket.send_json({"type": "ack", "received": data})

    except WebSocketDisconnect:
        if game_id in websocket_connections:
            websocket_connections[game_id].remove(websocket)
        print(f"Client disconnected from game {game_id}")


# ============================================================================
# Health Check
# ============================================================================


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "games_active": len(active_games),
        "connections": sum(len(conns) for conns in websocket_connections.values()),
        "active_sessions": session_manager.get_active_sessions_count(),
        "active_game_sessions": session_manager.get_active_games_count()
    }


@app.get("/stats")
async def get_stats(token: str = Depends(verify_token)):
    """Get server statistics (requires auth)."""
    return {
        "active_sessions": session_manager.get_active_sessions_count(),
        "active_games": session_manager.get_active_games_count(),
        "games": [{
            "game_id": game_id,
            "players": len(game_session.player_tokens),
            "max_players": game_session.max_players,
            "started": game_session.started
        } for game_id, game_session in session_manager.game_sessions.items()]
    }


@app.get("/games/list")
async def list_games(token: str = Depends(verify_token)):
    """List all available games (requires auth)."""
    games_list = []
    for game_id, game_session in session_manager.game_sessions.items():
        if game_id in active_games:
            games_list.append({
                "game_id": game_id,
                "players": len(game_session.player_tokens),
                "max_players": game_session.max_players,
                "started": game_session.started,
                "can_join": game_session.can_join(token)
            })
    return {"games": games_list}


if __name__ == "__main__":
    import uvicorn

    print("Starting Quantum Poker API...")
    print("API docs available at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
