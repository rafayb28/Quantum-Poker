"""
FastAPI Backend Structure (Skeleton for Future Implementation)

This file shows the planned API structure for the React frontend.
To run: uvicorn api_structure:app --reload
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum
import uuid

# Uncomment when ready to implement
# from .game import QuantumPoker

app = FastAPI(title="Quantum Poker API", version="0.1.0")

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


class CreateGameRequest(BaseModel):
    player_name: str
    num_players: int = 2


class JoinGameRequest(BaseModel):
    player_name: str


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
    community_cards: Dict[str, any]
    entanglements: Dict[str, List[tuple]]
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
    return {"message": "Quantum Poker API", "version": "0.1.0"}


@app.post("/game/create", response_model=Dict[str, str])
async def create_game(request: CreateGameRequest):
    """
    Create a new quantum poker game.
    """
    game_id = str(uuid.uuid4())

    # TODO: Initialize QuantumPoker instance
    # game = QuantumPoker(num_players=request.num_players)
    # games[game_id] = game

    games[game_id] = {
        "num_players": request.num_players,
        "players": [request.player_name],
        "status": "waiting",
    }

    return {"game_id": game_id, "message": "Game created successfully"}


@app.post("/game/{game_id}/join")
async def join_game(game_id: str, request: JoinGameRequest):
    """
    Join an existing game.
    """
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")

    game = games[game_id]

    # TODO: Add player to game
    # game.add_player(request.player_name)

    return {"message": f"{request.player_name} joined game {game_id}"}


@app.post("/game/{game_id}/start")
async def start_game(game_id: str):
    """
    Start the game (deal initial cards).
    """
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")

    game = games[game_id]

    # TODO: Start game logic
    # game.deal_hole_cards()
    # await broadcast_game_state(game_id)

    return {"message": "Game started"}


@app.get("/game/{game_id}/state", response_model=Dict)
async def get_game_state(game_id: str):
    """
    Get current state of the game.
    """
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")

    game = games[game_id]

    # TODO: Return actual game state
    # return game.get_game_state()

    return {"game_id": game_id, "status": "placeholder"}


@app.post("/game/{game_id}/action")
async def perform_action(game_id: str, request: PlayerActionRequest):
    """
    Perform a standard poker action (fold, check, call, raise).
    """
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")

    game = games[game_id]

    # TODO: Implement action logic
    # game.perform_action(player_id, request.action, request.amount)
    # await broadcast_game_state(game_id)

    return {"message": f"Action {request.action} performed"}


@app.post("/game/{game_id}/quantum-action")
async def perform_quantum_action(game_id: str, request: QuantumActionRequest):
    """
    Perform a quantum action (entanglement, etc.).
    """
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")

    game = games[game_id]

    # TODO: Implement quantum action
    # game.entangle_cards(player, request.source_card_idx, request.target_card_id, request.bit_index)
    # await broadcast_game_state(game_id)

    return {"message": f"Quantum action {request.action} performed"}


@app.get("/game/{game_id}/circuit")
async def get_circuit_diagram(game_id: str):
    """
    Get the quantum circuit diagram as SVG or text.
    """
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")

    game = games[game_id]

    # TODO: Return circuit visualization
    # circuit_text = game.get_circuit_diagram()
    # OR export as SVG for frontend

    return {"circuit": "placeholder circuit diagram"}


@app.post("/game/{game_id}/showdown")
async def trigger_showdown(game_id: str):
    """
    Trigger showdown (measure all cards).
    """
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")

    game = games[game_id]

    # TODO: Perform showdown
    # results = game.showdown()
    # await broadcast_game_state(game_id)

    return {"message": "Showdown complete", "results": {}}


# ============================================================================
# WebSocket for Real-time Updates
# ============================================================================


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
        while True:
            # Keep connection alive
            data = await websocket.receive_text()

            # Echo back for now (TODO: Handle client messages)
            await websocket.send_json({"type": "pong", "data": data})

    except WebSocketDisconnect:
        websocket_connections[game_id].remove(websocket)
        print(f"Client disconnected from game {game_id}")


async def broadcast_game_state(game_id: str):
    """
    Broadcast game state to all connected clients.
    """
    if game_id not in websocket_connections:
        return

    game = games.get(game_id)
    if not game:
        return

    # TODO: Get actual game state
    # state = game.get_game_state()

    state = {"type": "game_update", "game_id": game_id}

    # Send to all connected clients
    for websocket in websocket_connections[game_id]:
        try:
            await websocket.send_json(state)
        except:
            pass


# ============================================================================
# Health Check
# ============================================================================


@app.get("/health")
async def health_check():
    return {"status": "healthy", "games_active": len(games)}


if __name__ == "__main__":
    import uvicorn

    print("Starting Quantum Poker API...")
    print("API docs available at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
