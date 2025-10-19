import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const auth = {
  createSession: (username) => 
    api.post('/auth/session', { username }),
  
  validateSession: () => 
    api.get('/auth/validate'),
};

export const game = {
  create: (numPlayers = 2, maxPlayers = 6) => 
    api.post('/game/create', { num_players: numPlayers, max_players: maxPlayers }),
  
  join: (gameId) => 
    api.post(`/game/${gameId}/join`),
  
  leave: (gameId) =>
    api.post(`/game/${gameId}/leave`),
  
  start: (gameId) => 
    api.post(`/game/${gameId}/start`),
  
  getState: (gameId) => 
    api.get(`/game/${gameId}/state`),
  
  performAction: (gameId, action, amount = null) => 
    api.post(`/game/${gameId}/action`, { action, amount }),
  
  performQuantumAction: (gameId, action, sourceCardIdx, targetCardId, bitIndex) =>
    api.post(`/game/${gameId}/quantum-action`, {
      action,
      source_card_idx: sourceCardIdx,
      target_card_id: targetCardId,
      bit_index: bitIndex,
    }),
  
  nextRound: (gameId) => 
    api.post(`/game/${gameId}/next-round`),
  
  showdown: (gameId) => 
    api.post(`/game/${gameId}/showdown`),
};

export default api;
