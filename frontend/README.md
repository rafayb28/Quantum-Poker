# Quantum Poker Frontend

Minimal React frontend for testing Quantum Poker gameplay.

## Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on http://localhost:3000

## Requirements

- Backend API running on http://localhost:8000
- Node.js 18+

## Features

- Login with temporary username
- Create/join games
- View game state
- Make poker actions (fold, check, call)
- Real-time polling (2s interval)

## Architecture

- Vite + React
- Axios for API calls
- CSS for styling (no external UI libraries)
- Polling-based updates (no WebSocket yet)

## Development

The frontend proxies API requests to the backend:
- `/api/*` → `http://localhost:8000/*`

## Minimal Design

This is a testing UI with only essential features:
- No animations
- No quantum action UI yet
- No raise/all-in controls yet
- No entanglement visualization
- Basic polling instead of WebSocket

These will be added after core gameplay is validated.
