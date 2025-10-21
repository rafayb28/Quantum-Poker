# Quick Reference - Quantum Poker

## Start Playing (3 Steps)

### 1. Start Backend
```powershell
python main.py
```

### 2. Start Frontend
```powershell
cd frontend
npm run dev
```

### 3. Open Browser
- Go to `http://localhost:3000`
- Login with any username
- Create or join a game

## File Locations

### Key Files
- `main.py` - Backend entry point
- `src/game.py` - Core game logic
- `frontend/app/game/[gameId]/page.tsx` - Main game page
- `frontend/components/game/` - Game UI components

### Documentation
- `README.md` - Overview
- `TESTING.md` - Full testing guide
- `STATUS.md` - Current status
- `FRONTEND_COMPLETE.md` - Frontend details

## Ports

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- WebSocket: `ws://localhost:8000/ws/{gameId}/{token}`

## Testing

### Run Backend Tests
```powershell
pytest tests/ -v
```
Expected: 73 passed

### Run Full Game
1. Open two browsers (or incognito)
2. Login as different users
3. Player 1: Create game
4. Player 2: Join with game ID
5. Player 1: Start game
6. Play through betting rounds

## Common Commands

### Backend
```powershell
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Start server
python main.py
```

### Frontend
```powershell
# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build

# Type check
npm run type-check
```

## Game Flow

1. **Pre-flop**: Players dealt 2 cards, blinds posted
2. **Betting**: Fold/check/call/raise/all-in
3. **Flop**: 3 community cards revealed
4. **Betting**: Another round
5. **Turn**: 4th community card
6. **Betting**: Another round
7. **River**: 5th community card
8. **Betting**: Final round
9. **Showdown**: Best hand wins

## Quantum Actions

- Click "Quantum Entangle" button
- Select one of your cards
- Costs 1 quantum chip
- Affects rank only (bits 0-2)
- Collapses at showdown

## Keyboard Shortcuts

None currently implemented (all mouse-driven).

## Troubleshooting

### Backend won't start
- Check Python version (need 3.10+)
- Install requirements: `pip install -r requirements.txt`
- Check port 8000 not in use

### Frontend won't start
- Run `npm install` first
- Check Node version (need 18+)
- Check port 3000 not in use

### WebSocket disconnects
- Frontend auto-reconnects
- Check backend is running
- Look for errors in browser console

### Game not loading
- Check `.env.local` has correct URLs
- Verify both backend and frontend running
- Check browser console for errors

## Default Settings

- **Players**: 2-6 supported, default 2
- **Starting chips**: 1000 per player
- **Quantum chips**: 2 per player per hand
- **Small blind**: 10 chips
- **Big blind**: 20 chips

## API Endpoints

- `POST /auth/session` - Login
- `POST /game/create` - Create game
- `POST /game/{id}/join` - Join game
- `POST /game/{id}/start` - Start game
- `GET /game/{id}/state` - Get state
- `POST /game/{id}/action` - Perform action
- `POST /game/{id}/quantum-action` - Entangle

## Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## Tech Stack Quick Ref

**Backend:**
- FastAPI (web framework)
- Qiskit (quantum computing)
- pytest (testing)

**Frontend:**
- Next.js 14 (React framework)
- TypeScript (type safety)
- Tailwind (styling)
- Zustand (state)

## Status

✅ Backend complete (73/73 tests)  
✅ Frontend complete (0 errors)  
✅ Ready for testing

---

**Need help?** See `TESTING.md` for detailed guide.
