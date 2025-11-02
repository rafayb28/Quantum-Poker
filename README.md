# Quantum Poker

Texas Hold'em poker with quantum mechanics. Players can manipulate cards using quantum operations including superposition, phase interference, and entanglement. Cards collapse to definite values at showdown based on quantum measurement.

## Quick Start

### Backend Setup
```bash
pip install -r requirements.txt
cd src
uvicorn api:app --reload
```
Runs on `http://localhost:8000`

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Runs on `http://localhost:3000`

### Running Tests
```bash
pytest tests/ -v
```

### Demo Game
To see a command-line demonstration of quantum operations:
```bash
python main.py
```

## Features

### Poker Mechanics
- Full Texas Hold'em rules with all betting rounds (pre-flop, flop, turn, river, showdown)
- Complete betting actions: fold, check, call, raise, all-in
- Side pot management for complex all-in scenarios
- 2-6 player support
- Real-time updates via WebSocket

### Quantum Mechanics
- Three quantum operations: Superposition, Phase Interference, and Entanglement
- Quantum gates: H (Hadamard), RZ (Phase Rotation), CNOT (Entanglement)
- Manipulate rank bits 0-2 for strategic card variation
- Cards remain in superposition until showdown measurement
- 2 quantum chips allocated per player per hand

## Tech Stack

### Backend
- Python 3.10+
- FastAPI with Uvicorn
- Qiskit for quantum circuit simulation
- WebSocket for real-time communication
- pytest with 73 passing tests

### Frontend
- Next.js 14 with App Router
- TypeScript
- Tailwind CSS for styling
- Zustand for state management
- WebSocket client for real-time updates

## How Quantum Works

### Card Representation
Each card is a 6-bit register (0-51 encoding 52 cards):
- **Bits 0-3**: Rank (0-12 for Ace through King)
- **Bits 4-5**: Suit (0=Spades, 1=Diamonds, 2=Clubs, 3=Hearts)
- Invalid values (13-15 for rank, 52-63 overall) are rejected

### Quantum Operations

#### 1. Superposition
- Gate: Hadamard (H)
- Cost: 1 quantum chip
- Target: Own card only
- Effect: Puts a card bit into equal superposition, creating 50/50 probability of bit flip

#### 2. Phase Interference
- Gate: RZ(angle) with configurable rotation angle
- Cost: 1 quantum chip
- Angle: 0-360 degrees (adjustable via slider)
- Target: Own card only
- Effect: When combined with superposition (H-RZ-H sequence), controls quantum interference
  - 180 degrees: Guaranteed bit flip
  - Other angles: Biased probabilities toward specific outcomes
  - 0/360 degrees: No effect

#### 3. Entanglement
- Gates: Hadamard + CNOT (H+CNOT)
- Cost: 1 chip for own/community cards, 2 chips for opponent cards
- Target: Any card (own, community, or opponent)
- Effect: Creates quantum correlation between two cards so they change together

#### Bit Manipulation Impact
Only rank bits 0-2 can be manipulated (suit is immutable):
- Bit 0: Plus or minus 1 rank (example: 7 becomes 6 or 8)
- Bit 1: Plus or minus 2 ranks (example: 7 becomes 5 or 9)
- Bit 2: Plus or minus 4 ranks (example: 7 becomes 3 or 11)

### Measurement and Circuit Behavior

All cards exist in a shared quantum circuit managed by Qiskit. Cards remain in superposition throughout all betting rounds. At showdown, only cards that were affected by quantum operations are measured from the circuit using quantum simulation with 2048 shots. Unaffected cards retain their original dealt values. Measurement outcomes follow quantum probability distributions determined by the applied gates and operations.

## Project Structure

```
src/
  ├── api.py                # FastAPI routes
  ├── game.py               # Core poker logic
  ├── quantum_circuit.py    # Quantum operations
  ├── hand_evaluator.py     # Hand ranking
  ├── side_pot_manager.py   # Side pot handling
  └── session_manager.py    # Player sessions

frontend/
  ├── app/                  # Next.js pages
  ├── components/           # React components
  ├── store/                # Zustand state
  ├── hooks/                # Custom hooks
  └── lib/                  # API client

tests/                      # Backend tests (73 passing)
```

## API Endpoints

### Authentication
- POST /auth/session - Create player session and receive token
- GET /auth/validate - Validate session token

### Game Management
- POST /game/create - Create new game instance
- POST /game/{id}/join - Join existing game
- POST /game/{id}/start - Start game after all players joined
- GET /game/{id}/state - Get current game state
- POST /game/{id}/next-round - Advance to next betting round

### Game Actions
- POST /game/{id}/action - Perform betting action (fold, check, call, raise, all-in)
- POST /game/{id}/quantum-action - Perform quantum operation (superposition, phase, entanglement)
- POST /game/{id}/showdown - Trigger showdown and measure quantum states

### Real-Time Communication
- WebSocket endpoint: ws://localhost:8000/ws/{game_id}/{token}
- Broadcasts game state updates to all connected players

## Development

### Backend Development
Start the FastAPI server with auto-reload:
```bash
cd src
uvicorn api:app --reload
```

### Frontend Development
Start the Next.js development server:
```bash
cd frontend
npm run dev
```

### Testing
Run the full test suite:
```bash
pytest tests/ -v
```

## Additional Documentation

- docs/QUICKSTART.md - Detailed setup guide
- docs/ROADMAP.md - Development roadmap and future features
- docs/AUTHENTICATION.md - Session management details
- docs/FRONTEND_STRUCTURE.md - Frontend architecture overview

## License

MIT License
