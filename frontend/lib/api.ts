// API client for Quantum Poker backend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchWithAuth(url: string, options: RequestInit = {}) {
  // Only access localStorage on client-side
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers,
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    
    // If token is invalid/expired, clear storage and redirect to lobby (client-side only)
    if (response.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('token');
      sessionStorage.removeItem('player_number');
      window.location.href = '/lobby';
    }
    
    throw new ApiError(response.status, error.detail || 'Request failed');
  }
  
  return response.json();
}

export const api = {
  // Authentication
  async createSession(username: string) {
    return fetchWithAuth('/auth/session', {
      method: 'POST',
      body: JSON.stringify({ username }),
    });
  },
  
  async validateSession() {
    return fetchWithAuth('/auth/validate');
  },
  
  // Game management
  async createGame() {
    return fetchWithAuth('/game/create', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  },
  
  async joinGame(gameId: string) {
    return fetchWithAuth(`/game/${gameId}/join`, {
      method: 'POST',
    });
  },
  
  async leaveGame(gameId: string) {
    return fetchWithAuth(`/game/${gameId}/leave`, {
      method: 'POST',
    });
  },
  
  async startGame(gameId: string) {
    return fetchWithAuth(`/game/${gameId}/start`, {
      method: 'POST',
    });
  },
  
  async startNextHand(gameId: string) {
    return fetchWithAuth(`/game/${gameId}/next-hand`, {
      method: 'POST',
    });
  },
  
  async getGameState(gameId: string) {
    return fetchWithAuth(`/game/${gameId}/state`);
  },
  
  // Game actions
  async performAction(gameId: string, action: string, amount?: number) {
    return fetchWithAuth(`/game/${gameId}/action`, {
      method: 'POST',
      body: JSON.stringify({ action, amount }),
    });
  },
  
  async performQuantumAction(
    gameId: string,
    source_card_idx: number,
    target_card_id: string,
    bit_index: number
  ) {
    return fetchWithAuth(`/game/${gameId}/quantum-action`, {
      method: 'POST',
      body: JSON.stringify({
        action: 'entangle',
        source_card_idx,
        target_card_id,
        bit_index,
      }),
    });
  },
  
  async triggerShowdown(gameId: string) {
    return fetchWithAuth(`/game/${gameId}/showdown`, {
      method: 'POST',
    });
  },
  
  // Stats
  async listGames() {
    return fetchWithAuth('/games/list');
  },
};
