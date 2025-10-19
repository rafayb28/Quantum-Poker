# React Frontend Structure

## Tech Stack

- Frontend: Next.js 14+ (App Router) or Vite + React
- State: Zustand
- Styling: Tailwind CSS + Framer Motion
- WebSocket: Native WebSocket API or socket.io-client
- Quantum Viz: D3.js or SVG export from backend

## Project Structure

```
quantum-poker-frontend/
├── public/
│   ├── cards/
│   ├── sounds/
│   └── favicon.ico
├── src/
│   ├── app/ or pages/
│   │   ├── page.tsx
│   │   └── game/[id]/page.tsx
│   ├── components/
│   │   ├── Card/
│   │   ├── Table/
│   │   ├── Player/
│   │   ├── Quantum/
│   │   └── UI/
│   ├── hooks/
│   │   ├── useGameState.ts
│   │   ├── useWebSocket.ts
│   │   └── useQuantumActions.ts
│   ├── store/
│   │   ├── gameStore.ts
│   │   └── uiStore.ts
│   ├── services/
│   │   ├── api.ts
│   │   ├── websocket.ts
│   │   └── quantum.ts
│   ├── types/
│   └── utils/
```
│       └── globals.css
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── README.md
```

## Key Components Breakdown

### 1. Card Component (`Card.tsx`)

```typescript
interface CardProps {
  rank: string;
  suit: string;
  identifier: string;
  isRevealed: boolean;
  isEntangled: boolean;
  entangledWith?: string[];
  onClick?: () => void;
  className?: string;
}

// Features:
// - Display card with rank/suit or back
// - Show entanglement indicator (glowing border?)
// - Animate on flip/measurement
// - Quantum superposition visual effect
```

### 2. Quantum Circuit Viewer (`QuantumCircuitViewer.tsx`)

```typescript
interface QuantumCircuitViewerProps {
  gameId: string;
  circuitData: string | SVG; // From backend
  entanglements: EntanglementGraph;

## Key Components

### Card Component
Display quantum state, show entanglement, animate collapse.

### Quantum Circuit Viewer
Display circuit diagram, highlight qubits, show entanglement connections.

### Entanglement Selector
Choose source/target cards, select bit to entangle, preview effect, display cost.

### Poker Table
SVG table with player seats, community cards, pot display, animations.

### Player Actions
Fold/check/call/raise buttons, bet slider, quantum action button.

## State Management

Game store handles: gameId, players, cards, pot, bets, entanglements.
UI store handles: circuit visibility, selected cards, notifications.

## WebSocket Integration

Connect to backend, handle game updates, player actions, quantum actions, measurements.

## Visualization Options

1. Backend SVG Export: Accurate but less interactive
2. D3.js Custom: Fully interactive, complex implementation
3. Three.js 3D: Visually stunning, performance concerns

Recommended: Hybrid approach with SVG for details and D3.js for live game.

## Animations

Card animations: Deal, entangle glow, measurement flip.
Entanglement visuals: Animated gradient lines between cards.
```

## Responsive Design Considerations

- Desktop: Full table view with circuit panel on side
- Tablet: Stacked layout, circuit as modal
- Mobile: Simplified view, essential actions only, circuit accessible via button

## Accessibility

- ARIA labels for all interactive elements
- Keyboard navigation for all actions
- Screen reader descriptions for quantum states
- High contrast mode support
- Reduced motion option

## Performance Optimizations

- Lazy load circuit visualization
- Virtualize player list for large games
- Memoize expensive calculations (hand evaluation)
- Debounce WebSocket updates
- Use CSS transforms for animations (GPU acceleration)

## Quick Start Commands

```bash
# Create Next.js app
npx create-next-app@latest quantum-poker-frontend --typescript --tailwind --app

# OR Create Vite app
npm create vite@latest quantum-poker-frontend -- --template react-ts

# Install dependencies
cd quantum-poker-frontend
npm install zustand framer-motion d3 @types/d3

# Optional: Socket.io
npm install socket.io-client

# Development
npm run dev
```

## Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## Integration Flow

1. **Game Creation**
   ```typescript
   const { gameId } = await api.createGame(playerName, numPlayers);
   router.push(`/game/${gameId}`);
   ```

2. **WebSocket Connection**
   ```typescript
   useEffect(() => {
     connectWebSocket(gameId);
   }, [gameId]);
   ```

3. **Receiving Updates**
   ```typescript
   ws.onmessage = (event) => {
     const update = JSON.parse(event.data);
     updateGameState(update);
   };
   ```

4. **Sending Actions**
   ```typescript
   const handleBet = async (amount: number) => {
     await api.performAction(gameId, { action: 'raise', amount });
     // State updates via WebSocket
   };
   ```

5. **Quantum Actions**
   ```typescript
   const handleEntangle = async (source: number, target: string, bit: number) => {
     await api.performQuantumAction(gameId, {
       action: 'entangle',
       source_card_idx: source,
       target_card_id: target,
       bit_index: bit
     });
     // Show animation, wait for WebSocket confirmation
   };
   ```
