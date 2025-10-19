"""
FastAPI Backend for Quantum Poker

To run: uvicorn src.api:app --reload
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum
import uuid

from .game import QuantumPoker

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
    return {"message": "Quantum Poker API", "version": "0.1.0", "status": "operational"}


@app.post("/game/create", response_model=Dict[str, str])
async def create_game(request: CreateGameRequest):
    """
    Create a new quantum poker game.
    """
    game_id = str(uuid.uuid4())
    
    # Initialize QuantumPoker instance
    game = QuantumPoker(num_players=request.num_players)
    active_games[game_id] = game
    game_players[game_id] = {1: request.player_name}
    
    # Set player name
    game.players[0].name = request.player_name

    return {
        "game_id": game_id,
        "player_number": "1",
        "message": "Game created successfully"
    }


@app.post("/game/{game_id}/join")
async def join_game(game_id: str, request: JoinGameRequest):
    """
    Join an existing game.
    """
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")

    game = active_games[game_id]
    players_in_game = len(game_players[game_id])
    
    if players_in_game >= game.num_players:
        raise HTTPException(status_code=400, detail="Game is full")
    
    # Assign next player number
    player_number = players_in_game + 1
    game_players[game_id][player_number] = request.player_name
    game.players[player_number - 1].name = request.player_name

    return {
        "message": f"{request.player_name} joined game {game_id}",
        "player_number": player_number
    }


@app.post("/game/{game_id}/start")
async def start_game(game_id: str):
    """
    Start the game (deal initial cards, post blinds).
    """
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = active_games[game_id]
    
    if len(game_players[game_id]) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 players to start")
    
    # Deal hole cards and post blinds
    game.deal_hole_cards()
    game.post_blinds()
    game.current_round = "pre-flop"
    
    return {
        "message": "Game started",
        "state": game.to_dict()
    }


@app.get("/game/{game_id}/state")
async def get_game_state(game_id: str, player_number: Optional[int] = None):
    """
    Get current state of the game.
    """
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")

    game = active_games[game_id]
    return game.to_dict(viewing_player=player_number)


@app.post("/game/{game_id}/action")
async def perform_action(game_id: str, player_number: int, request: PlayerActionRequest):
    """
    Perform a standard poker action (fold, check, call, raise).
    """
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")

    game = active_games[game_id]
    
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
async def perform_quantum_action(game_id: str, player_number: int, request: QuantumActionRequest):
    """
    Perform a quantum action (entanglement, etc.).
    """
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")

    game = active_games[game_id]
    
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
async def get_circuit_diagram(game_id: str):
    """
    Get the quantum circuit diagram as text.
    """
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")

    game = active_games[game_id]
    circuit_diagram = game.get_circuit_diagram()

    return {"circuit": circuit_diagram}


@app.post("/game/{game_id}/showdown")
async def trigger_showdown(game_id: str):
    """
    Trigger showdown (measure all cards).
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
async def advance_round(game_id: str):
    """
    Advance to the next round (flop, turn, river).
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
        "connections": sum(len(conns) for conns in websocket_connections.values())
    }


if __name__ == "__main__":
    import uvicorn

    print("Starting Quantum Poker API...")
    print("API docs available at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
