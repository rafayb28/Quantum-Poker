# Quick Start Guide

## Current Status

- Card encoding system (6 qubits per card)
- Global quantum circuit manager
- Entanglement implementation (H + CNOT)
- Game flow (deal, flop, turn, river, showdown)
- API structure for React frontend

## Setup

### Install Dependencies

```powershell
pip install -r requirements.txt
```

### Run Demo Game

```powershell
python main.py
```

This runs a 2-player demo with:
- Dealing hole cards
- Flop, turn, river
- Entanglement between cards
- Showdown with measurement

### Test Quantum Circuit

```powershell
python tests/test_quantum.py
```

Example usage:

```python
from src.quantum_circuit import QuantumPokerCircuit
from src.card import Card

qc = QuantumPokerCircuit()

card1 = Card("Hearts", "Ace")
card2 = Card("Spades", "King")

qc.add_card(card1, "P1H1")
qc.add_card(card2, "F0")

qc.entangle_cards("P1H1", "F0", bit_index=2)

print(qc.get_circuit_diagram())

# Simulate
qc.prepare_measurement()
qc.measure_all_cards()
results = qc.simulate(shots=100)

print("\nMeasurement results:")
for bitstring, count in results.items():
    print(f"{bitstring}: {count}")
```

### 4. Run API Server (Optional)

```powershell
uvicorn api_structure:app --reload
```

Access API docs at: http://localhost:8000/docs

## Next Steps (Prioritized)

### Week 1: Core Quantum Fixes
1. **Test the new global circuit system**
   ```powershell
   python game.py
   ```
   
2. **Add validation for measured cards**
   - Ensure rank values are 1-13 (not 0, 14-15)
   - Handle invalid measurements

3. **Implement additional entanglement options (2-5)**
   - Design different quantum strategies
   - Test their effects on game outcomes

### Week 2: Game Logic
1. **Add betting rounds**
   - Implement fold/check/call/raise
   - Add pot management
   - Handle side pots

2. **Implement hand evaluation**
   - Create hand ranking system
   - Determine winners
   - Handle ties

### Week 3: API Development
1. **Integrate game.py with api_structure.py**
   - Replace placeholder endpoints with real logic
   - Add session management
   - Test with Postman/curl

2. **Add WebSocket real-time updates**
   - Broadcast game state changes
   - Handle player actions
   - Test with multiple clients

### Week 4: React Frontend
1. **Set up React project**
   ```powershell
   npx create-next-app@latest quantum-poker-frontend --typescript --tailwind
   ```

2. **Build core components**
   - Poker table layout
   - Card components
   - Player actions

3. **Integrate with API**
   - API service layer
   - WebSocket connection
   - State management

## File Structure Overview

```
Quantum-Poker/
├── card.py                 # Card class with quantum register
├── player.py              # Player data model
├── quantum_circuit.py     # NEW: Global circuit manager
├── game.py               # NEW: Main game logic with quantum integration
├── api_structure.py      # NEW: FastAPI backend skeleton
├── main.py               # OLD: Simple demo (can be replaced)
├── test.py               # Quantum swap experiment
├── requirements.txt      # NEW: Python dependencies
├── README.md            # Your original spec
├── ROADMAP.md           # NEW: Development roadmap
└── FRONTEND_STRUCTURE.md # NEW: React architecture guide
```

## Testing Strategy

### Unit Tests (Create `tests/` folder)

```python
# tests/test_card.py
def test_card_encoding():
    card = Card("Hearts", "Ace")
    assert card.to_bits() == 0b110001  # 11 (Hearts) + 0001 (Ace)

# tests/test_entanglement.py
def test_entangle_cards():
    qc = QuantumPokerCircuit()
    # ... test entanglement logic

# tests/test_game.py
def test_deal_cards():
    game = QuantumPoker(num_players=2)
    game.deal_hole_cards()
    assert len(game.players[0].hand) == 2
```

Run tests:
```powershell
pytest tests/
```

## Common Issues & Solutions

### Issue 1: Invalid Rank Measured
**Problem**: Measurement gives rank 0, 14, or 15
**Solution**: Add post-measurement validation and re-sample

### Issue 2: Circuit Too Large
**Problem**: Too many qubits for simulation
**Solution**: Use statevector simulator or reduce players

### Issue 3: Entanglement Not Visible
**Problem**: Can't see effect of entanglement
**Solution**: Run more shots (1024+) or test with specific initial states

## Resources

### Qiskit Documentation
- [Quantum Circuit](https://qiskit.org/documentation/stubs/qiskit.circuit.QuantumCircuit.html)
- [Entanglement Tutorial](https://qiskit.org/textbook/ch-gates/multiple-qubits-entangled-states.html)

### Poker Rules
- [Texas Hold'em Rules](https://www.pokernews.com/poker-rules/texas-holdem.htm)
- [Hand Rankings](https://www.cardplayer.com/rules-of-poker/hand-rankings)

### FastAPI
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [WebSocket Support](https://fastapi.tiangolo.com/advanced/websockets/)

### React/Next.js
- [Next.js Documentation](https://nextjs.org/docs)
- [Zustand State Management](https://zustand-demo.pmnd.rs/)

## Contributing

As you develop:
1. Keep `ROADMAP.md` updated with completed tasks
2. Add comments explaining quantum operations
3. Document API endpoints as you implement them
4. Create example code for complex features

## Questions to Consider

1. **Quantum Strategy**:
   - What should entanglement options 2-5 do?
   - Should there be quantum "power-ups"?
   - How to balance quantum vs classical play?

2. **Game Balance**:
   - How many quantum chips per player?
   - Can quantum chips be earned/bought?
   - Should entanglement cost scale with pot size?

3. **UI/UX**:
   - How to explain quantum mechanics to non-physics players?
   - Should there be a tutorial mode?
   - How to visualize superposition before measurement?

4. **Technical**:
   - Max number of players before circuit becomes too large?
   - Should we use real quantum hardware (IBM Quantum)?
   - How to persist game state between sessions?

## Contact & Support

As you continue development, feel free to ask:
- "How do I implement [specific quantum feature]?"
- "How should the frontend visualize [quantum concept]?"
- "What's the best way to structure [API endpoint]?"

Good luck with your Quantum Poker game! 🃏⚛️
