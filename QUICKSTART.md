# Quick Start Guide - Testing Quantum Poker

## Step 1: Start Backend

```bash
# From project root
pip install -r requirements.txt
python -m uvicorn src.api:app --reload --port 8000
```

Backend runs on http://localhost:8000

## Step 2: Start Frontend

```bash
# Open new terminal
cd frontend
npm install
npm run dev
```

Frontend runs on http://localhost:3000

## Step 3: Test the Game

### Create a Game (Player 1)
1. Open http://localhost:3000
2. Enter username (e.g., "Alice")
3. Click "Create Game"
4. Copy the Game ID from the URL or screen

### Join the Game (Player 2)
1. Open http://localhost:3000 in new browser/tab
2. Enter different username (e.g., "Bob")
3. Click "Join Existing Game"
4. Paste the Game ID
5. Click "Join Game"

### Start Playing
1. Player 1 clicks "Start Game"
2. Game deals hole cards
3. Players take turns:
   - Fold: Give up hand
   - Check: Pass (if no bet to match)
   - Call: Match current bet
4. Click round advance buttons:
   - "Deal Flop" → 3 community cards
   - "Deal Turn" → 4th community card
   - "Deal River" → 5th community card
   - "Showdown" → Determine winner

## Current Limitations

This is a minimal testing UI:
- No raise/all-in controls yet
- No quantum action buttons yet
- No animations
- Basic polling (2s updates) instead of WebSocket
- Simple error handling

## Testing Checklist

- [ ] Login works with username
- [ ] Create game generates Game ID
- [ ] Second player can join with Game ID
- [ ] Start game button works (player 1 only)
- [ ] Hole cards display after start
- [ ] Players can fold/check/call
- [ ] Turn indicator shows correctly
- [ ] Flop/Turn/River deal community cards
- [ ] Showdown determines winner
- [ ] Pot and chip counts update

## Troubleshooting

**Frontend won't start:**
- Make sure Node.js 18+ installed
- Delete `node_modules` and `package-lock.json`, run `npm install` again

**Can't connect to backend:**
- Check backend is running on port 8000
- Check browser console for CORS errors

**Game state not updating:**
- Frontend polls every 2 seconds
- Check Network tab in browser DevTools
- Verify auth token in localStorage

**API errors:**
- Check backend logs for error details
- Verify token hasn't expired (60min timeout)

## Next Steps

Once basic gameplay works:
1. Add raise/all-in controls
2. Add quantum entanglement UI
3. Add WebSocket for real-time updates
4. Add circuit visualization
5. Add better error handling
6. Add animations and polish
