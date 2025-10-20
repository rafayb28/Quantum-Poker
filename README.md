# Quantum Poker# Quantum Poker



Poker game with quantum mechanics. Cards can be entangled and superposed.A Texas Hold'em poker game with quantum entanglement mechanics.



## Run It## Quick Start



```bash```bash

# Backendpip install -r requirements.txt

python -m uvicorn src.api:app --reloadpython main.py

```

# Frontend (separate terminal)

cd frontend && npm run dev## Project Structure

```

```

Visit http://localhost:3000Quantum-Poker/

├── src/                    # Core source code

## Play├── tests/                  # Test suite

├── examples/               # Usage examples

1. Player 1: Create game├── docs/                   # Documentation

2. Player 2: Join with Game ID  ├── main.py                 # Entry point

3. Start game and play poker└── requirements.txt        # Dependencies

```

## Features

## How It Works

**Working:**

- All poker actions (fold, check, call, raise, all-in)### Card Representation

- Full betting rounds (pre-flop → flop → turn → river)

- 2-player games# 1 | Representation of cards

- Backend: 73/73 tests ✅- Definition: A hole card is any of the two private cards held by each player. Community cards are the public cards dealt in the flop, turn, and river.

- Frontend: 7/7 tests ✅- 1.1: Each card is its own register containing 6 bits (0-64) with 0-51 used to encode the 52 cards.

    - Values 52-64 must be enforced to be invalid.

**Quantum (backend done, UI needed):**- 1.2: Bits 0-3 (0-15) used to represent value of card (A,2,...,Q,K).

- Entangle cards to link their values    - The values of 13-15 must be enforced to be invalid.

- Cards in superposition until showdown- 1.3: The remaining 2 bits are used to represent the suit: 00 = spades, 01 = diamonds, 10 = clubs, 11 = hearts

- Spend Q-chips to entangle- 1.4: All registers shall be part of a global circuit, where each card is its own slice within the circuit.

    - There will be a global dictionary containing a card identifier and the register for that card within the global circuit. Community cards are identified by F0, F1, F2, T, and R. Hole cards are identified by PxHx for a *player x* and *hole card x*.

## Structure    - There will be another global dictionary containing an ancilla bit identifier (A0, A1, ...) and its index within the global circuit.

- 1.5: All registers remain unmeasured until showdown.

```

src/          Backend (Python/FastAPI)# 2 | Entanglement

frontend/     UI (React)- 2.1: You may entangle your card with any other card, including community cards.

tests/        Backend tests    - **Entanglement is restricted to rank bits only (bits 0-2), not suit bits, to maintain poker strategy**

frontend/e2e/ E2E tests    - Option 1: Entangle one bit of your cards rank encoding with one bit of the other cards rank encoding. The source and target bits are the same.

```        - **Bit 0**: ±1 rank variation (minimal change - e.g., 7 ↔ 6 or 8)

        - **Bit 1**: ±2 rank variation (moderate change - e.g., 7 ↔ 5 or 9)

## Status        - **Bit 2**: ±4 rank variation (significant change - e.g., 7 ↔ 3 or 11)



See **FIXES_APPLIED.md** for latest updates.    $$\text{Given two states} \ket{A}, \ket{B} \text{we can entangle one qubit of each state, } x. \\ \text{1. Apply H onto } \ket{A_x} \\ \text{2. Apply } CNOT_{A_x \rightarrow B_x}$$



Game is fully playable. Quantum UI needs implementation.    - Option 2: TBD

    - Option 3: TBD
    - Option 4: TBD
    - Option 5: TBD

##  Features

-  **Quantum Card Encoding**: Each card represented by 6 qubits (4 for rank, 2 for suit)
-  **Entanglement System**: Players can entangle their cards with community cards
-  **Global Quantum Circuit**: All cards exist in a single quantum circuit
-  **Measurement & Collapse**: Cards collapse to classical values at showdown
-  **Quantum Error Handling**: Invalid measurements handled gracefully
-  **Betting Rounds**: Coming soon
-  **Hand Evaluation**: Coming soon
-  **REST API**: FastAPI backend for frontend integration
-  **React Frontend**: Interactive UI with circuit visualization

##  Usage

### Basic Game

```python
from src import QuantumPoker

## Card Encoding

Each card uses 6 qubits: 4 bits for rank (Ace-King), 2 bits for suit.

## Entanglement

Players can entangle their cards with community cards using quantum chips. Entanglement affects rank only:
- Bit 0: +/- 1 rank variation
- Bit 1: +/- 2 rank variation
- Bit 2: +/- 4 rank variation

## Usage

```python
from src import QuantumPoker

game = QuantumPoker(num_players=2)
game.deal_hole_cards()
game.deal_flop()

game.entangle_cards(
    player=game.players[0],
    source_card_idx=0,
    target_card_id="F0",
    bit_index=1
)

game.deal_turn()
game.deal_river()
result = game.showdown()
```

## Running Tests

```bash
python tests/test_quantum.py
python tests/test_entanglement_validation.py
```

## Technology

- Qiskit for quantum computing
- Python 3.10+
- FastAPI (planned for backend)
- React (planned for frontend)

## Documentation

- [docs/ROADMAP.md](docs/ROADMAP.md) - Development plan
- [docs/QUICKSTART.md](docs/QUICKSTART.md) - Setup guide
- [docs/FRONTEND_STRUCTURE.md](docs/FRONTEND_STRUCTURE.md) - Frontend design
- [docs/ISSUES_AND_SOLUTIONS.md](docs/ISSUES_AND_SOLUTIONS.md) - Technical decisions

## License

MIT License
