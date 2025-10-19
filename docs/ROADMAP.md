# Development Roadmap

## Phase 1: Core Quantum Logic (Current Priority)

### 1.1 Fix Card & Circuit Management
- [x] Create global QuantumCircuit in Poker class
- [x] Implement card identifier system (F0, F1, F2, T, R for community; P1H1, P1H2, etc.)
- [x] Create global dictionaries: card_register_map and ancilla_register_map
- [x] Refactor Card class to reference slices in global circuit

### 1.2 Implement Entanglement System
- [x] Add entangle() method to Card or Poker class
- [x] Implement Option 1: H + CNOT entanglement between card bits
- [ ] Design and implement Options 2-5 (different entanglement strategies)
- [x] Add validation to prevent invalid entanglements
- [x] Track entanglement relationships

### 1.3 Measurement & Collapse
- [x] Implement showdown measurement logic
- [x] Add card collapse mechanism
- [x] Handle entangled card collapses
- [x] Validate measured values

## Phase 2: Complete Poker Game Logic

### 2.1 Game Flow
- [ ] Implement betting rounds (pre-flop, flop, turn, river)
- [x] Add deal methods for community cards (flop, turn, river)
- [ ] Implement fold/check/call/raise/all-in actions
- [ ] Add pot management (main pot, side pots)
- [x] Implement showdown logic

### 2.2 Hand Evaluation
- [ ] Create hand ranking system (high card → royal flush)
- [ ] Implement winner determination
- [ ] Handle split pots
- [ ] Add kicker logic

### 2.3 Quantum Actions
- [ ] Design quantum chip economy
- [ ] Implement quantum action costs
- [ ] Add quantum superposition moves
- [ ] Create quantum bluffing mechanics

## Phase 3: Backend API Architecture

### 3.1 API Design
- [x] Choose framework (FastAPI)
- [x] Design RESTful endpoints
- [x] Implement WebSocket for real-time updates

### 3.2 State Management
- [ ] Design game state serialization
- [ ] Implement database/persistence
- [ ] Add session management
- [ ] Create quantum state snapshots for debugging

### 3.3 Security & Validation
- [ ] Add input validation
- [ ] Implement authentication (JWT?)
- [ ] Add rate limiting
- [ ] Validate quantum operations

## Phase 4: React Frontend Planning

### 4.1 Architecture
- [ ] Choose: Next.js (SSR) vs Vite+React (SPA)
- [ ] State management: Zustand or Redux Toolkit
- [ ] WebSocket client for real-time updates
- [ ] Component structure design

### 4.2 Core Components
```
src/
├── components/
│   ├── Card/
│   │   ├── Card.tsx (display card with quantum state)
│   │   ├── CardBack.tsx
│   │   └── EntanglementVisual.tsx
│   ├── Table/
│   │   ├── PokerTable.tsx
│   │   ├── CommunityCards.tsx
│   │   └── Pot.tsx
│   ├── Player/
│   │   ├── PlayerHand.tsx
│   │   ├── PlayerInfo.tsx
│   │   └── PlayerActions.tsx
│   ├── QuantumUI/
│   │   ├── CircuitVisualization.tsx (using qiskit-viz or custom)
│   │   ├── EntanglementSelector.tsx
│   │   └── QuantumChipDisplay.tsx
│   └── Game/
│       ├── BettingControls.tsx
│       └── GameLog.tsx
├── hooks/
│   ├── useGameState.ts
│   ├── useWebSocket.ts
│   └── useQuantumActions.ts
├── services/
│   ├── api.ts
│   └── websocket.ts
└── types/
    ├── game.types.ts
    └── quantum.types.ts
```

### 4.3 Visualization Challenges
- [ ] Decide on circuit visualization library (qiskit-viz export? D3.js custom?)
- [ ] Design entanglement representation (visual links between cards?)
- [ ] Show superposition states before collapse
- [ ] Animate measurement/collapse events
- [ ] Display probability distributions

### 4.4 UX/UI Considerations
- [ ] Tutorial system for quantum mechanics
- [ ] Tooltips explaining quantum actions
- [ ] Visual feedback for entanglement
- [ ] Responsive design for mobile
- [ ] Accessibility features

## Phase 5: Advanced Features

### 5.1 Quantum Mechanics
- [ ] Additional entanglement options (2-5 from README)
- [ ] Quantum teleportation moves?
- [ ] Measurement interference?
- [ ] Quantum gates as power-ups?

### 5.2 Game Modes
- [ ] Practice mode vs AI
- [ ] Multiplayer lobbies
- [ ] Tournament mode
- [ ] Quantum tutorial mode

### 5.3 Analytics & Visualization
- [ ] Game replay system
- [ ] Statistical analysis
- [ ] Circuit history viewer
- [ ] Probability calculator

## Immediate Action Items (This Week)

1. **Fix Global Circuit Architecture** - Most critical
   - Refactor to use single global circuit
   - Implement card identifier system
   
2. **Implement Basic Entanglement**
   - Add entangle method (Option 1: H + CNOT)
   - Test with simple 2-player scenario

3. **Add Game Flow Skeleton**
   - Implement deal_flop(), deal_turn(), deal_river()
   - Add basic betting round structure
   
4. **Start API Planning**
   - Create requirements.txt with FastAPI
   - Design initial endpoint structure

## Technology Stack Recommendations

### Backend
- **Framework**: FastAPI (async Python, auto-docs, WebSocket support)
- **Quantum**: Qiskit (already using)
- **Database**: PostgreSQL (game history) + Redis (sessions)
- **Real-time**: WebSocket (Socket.IO or FastAPI WebSocket)

### Frontend
- **Framework**: Next.js 14+ (App Router)
- **State**: Zustand (simpler than Redux for real-time games)
- **Styling**: Tailwind CSS + Framer Motion (animations)
- **Quantum Viz**: 
  - Option 1: Export Qiskit circuits as SVG from backend
  - Option 2: D3.js custom visualization
  - Option 3: Three.js for 3D circuit representation

### DevOps
- **Container**: Docker
- **Deployment**: Vercel (frontend) + Railway/Render (backend)
- **CI/CD**: GitHub Actions
