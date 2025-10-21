# Quantum Poker

Texas Hold'em poker with quantum entanglement mechanics. Cards can be superposed and entangled, collapsing to definite values only at showdown.

## Quick Start

### Backend
```bash
pip install -r requirements.txt
python main.py
```
Runs on `http://localhost:8000`

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Runs on `http://localhost:3000`

See [TESTING.md](TESTING.md) for detailed testing instructions.

## Features

**Poker Mechanics:**
- Full Texas Hold'em rules (pre-flop, flop, turn, river, showdown)
- All betting actions (fold, check, call, raise, all-in)
- Side pots for all-in scenarios
- 2-6 player support
- Real-time WebSocket updates

**Quantum Mechanics:**
- Quantum entanglement between player cards
- H+CNOT gates on rank bits (0-2)
- Superposition maintained until showdown
- 2 quantum chips per player per hand

## Tech Stack

**Backend:**
- Python 3.10+
- FastAPI (REST API)
- Qiskit (quantum circuits)
- pytest (73 tests passing)

**Frontend:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Zustand (state management)
- WebSocket (real-time)

## How Quantum Works

### Card Representation
Each card is a 6-bit register (0-51 encoding 52 cards):
- **Bits 0-3**: Rank (0-12 for Ace through King)
- **Bits 4-5**: Suit (0=Spades, 1=Diamonds, 2=Clubs, 3=Hearts)
- Invalid values (13-15 for rank, 52-63 overall) are rejected

### Entanglement Mechanics

Players can entangle their hole cards with opponent cards using quantum chips:

1. **Cost**: 1 quantum chip per entanglement
2. **Target**: Any opponent's hole card
3. **Bits affected**: Rank bits 0-2 only (suit remains unchanged)
4. **Operation**: Hadamard gate + CNOT gate creates superposition

**Impact levels:**
- **Bit 0**: ±1 rank variation (e.g., 7 ↔ 6 or 8)
- **Bit 1**: ±2 rank variation (e.g., 7 ↔ 5 or 9)  
- **Bit 2**: ±4 rank variation (e.g., 7 ↔ 3 or 11)

### Quantum Circuit

$$\text{Given two states } |A\rangle, |B\rangle \text{ we entangle qubit } x: \\
\text{1. Apply H onto } |A_x\rangle \\
\text{2. Apply } \text{CNOT}_{A_x \rightarrow B_x}$$

All cards exist in a global quantum circuit. Cards are measured only at showdown, collapsing superposition to definite values.

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
- `POST /auth/session` - Create session
- `GET /auth/validate` - Validate token

### Game Management
- `POST /game/create` - Create game
- `POST /game/{id}/join` - Join game
- `POST /game/{id}/start` - Start game
- `GET /game/{id}/state` - Get state

### Actions
- `POST /game/{id}/action` - Perform action (fold/check/call/raise/all-in)
- `POST /game/{id}/quantum-action` - Entangle cards
- `POST /game/{id}/showdown` - Trigger showdown

### WebSocket
- `ws://localhost:8000/ws/{game_id}/{token}` - Real-time updates

## Development

### Run Tests
```bash
pytest tests/ -v
```

### Run Backend
```bash
python main.py
```

### Run Frontend
```bash
cd frontend
npm run dev
```

## Documentation

- [TESTING.md](TESTING.md) - Complete testing guide
- [docs/QUICKSTART.md](docs/QUICKSTART.md) - Setup instructions
- [docs/ROADMAP.md](docs/ROADMAP.md) - Development roadmap

## License

MIT License
